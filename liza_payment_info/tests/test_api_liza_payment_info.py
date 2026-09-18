# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# API documentation: https://docs.liza.nl
# For cassette instructions, see liza_base/tests/common.py.

from unittest.mock import patch

from freezegun import freeze_time

from odoo import Command
from odoo.tools import mute_logger

from odoo.addons.liza_base.tests.common import LizaTestCommon

from ..liza_utils import liza_send_open_invoices

PAYEX_URL = "https://autopayex.liza.nl/V4.0/AutoPayex.asmx"


class TestApiLizaPaymentInfo(LizaTestCommon):
    LIZA_ALLOWED_HOSTNAMES = ("autopayex.liza.nl",)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company.write(
            {
                "country_id": cls.env.ref("base.be").id,
                "company_registry": "0869703978",
            }
        )
        # Minimal accounting setup so the tests do not depend on a chart of
        # accounts / localization being installed (needed on a bare Community).
        cls.income_account = cls.env["account.account"].create(
            {
                "name": "Test Income",
                "code": "TINC",
                "account_type": "income",
                "company_ids": [Command.set(cls.company.ids)],
            }
        )
        cls.receivable_account = cls.env["account.account"].create(
            {
                "name": "Test Receivable",
                "code": "TREC",
                "account_type": "asset_receivable",
                "reconcile": True,
                "company_ids": [Command.set(cls.company.ids)],
            }
        )
        cls.sale_journal = cls.env["account.journal"].create(
            {
                "name": "Test Sales",
                "code": "TSAL",
                "type": "sale",
                "company_id": cls.company.id,
            }
        )
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Test Customer BE",
                "is_company": True,
                "country_id": cls.env.ref("base.be").id,
                "company_registry": "0405056855",
                "property_account_receivable_id": cls.receivable_account.id,
            }
        )

    def _set_credentials(self):
        self.env["ir.config_parameter"].sudo().set_param("liza.payex.url", PAYEX_URL)
        return super()._set_credentials()

    def _create_open_invoice(
        self, partner=None, amount=1000.0, invoice_date="2026-06-01"
    ):
        partner = partner or self.customer
        if not partner.property_account_receivable_id:
            partner.property_account_receivable_id = self.receivable_account
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "journal_id": self.sale_journal.id,
                "invoice_date": invoice_date,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Test Service",
                            "quantity": 1,
                            "price_unit": amount,
                            "account_id": self.income_account.id,
                            "tax_ids": [Command.clear()],
                        }
                    )
                ],
            }
        )
        invoice.action_post()
        return invoice

    @freeze_time("2026-07-03")
    def test_cron_send_open_invoices(self):
        self._set_credentials()
        self.company.liza_payment_info_enable = True
        invoice = self._create_open_invoice()
        self.assertEqual(invoice.payment_state, "not_paid")

        vals = invoice._liza_prepare_invoice_values()
        self.assertEqual(vals["InvoiceNumber"], invoice.name)
        self.assertEqual(vals["InvoiceDate"], "20260601")
        self.assertEqual(vals["CustomerCountry"], "BE")
        self.assertEqual(vals["CustomerIdentifierType"], "RegistrationNumber")
        self.assertEqual(vals["CustomerIdentifier"], self.customer.company_registry)
        self.assertEqual(vals["OpenAmountWhole"], str(int(invoice.amount_residual)))

        self.env["account.move"]._cron_liza_send_open_invoices()

    def test_prepare_invoice_skips_missing_identifier(self):
        partner = self.env["res.partner"].create(
            {
                "name": "No ID Customer",
                "is_company": True,
                "country_id": self.env.ref("base.be").id,
            }
        )
        invoice = self._create_open_invoice(partner=partner)
        self.assertIsNone(invoice._liza_prepare_invoice_values())

    def test_prepare_invoice_uses_vat_when_no_registry(self):
        partner = self.env["res.partner"].create(
            {
                "name": "VAT Customer",
                "is_company": True,
                "country_id": self.env.ref("base.be").id,
                "vat": "BE0405056855",
            }
        )
        invoice = self._create_open_invoice(partner=partner)
        vals = invoice._liza_prepare_invoice_values()
        self.assertEqual(vals["CustomerIdentifierType"], "VatNumber")
        self.assertEqual(vals["CustomerIdentifier"], partner.vat)

    def test_prepare_invoice_skips_unsupported_country(self):
        partner = self.env["res.partner"].create(
            {
                "name": "UK Customer",
                "is_company": True,
                "country_id": self.env.ref("base.uk").id,
                "company_registry": "12345678",
            }
        )
        invoice = self._create_open_invoice(partner=partner)
        self.assertIsNone(invoice._liza_prepare_invoice_values())

    @patch("odoo.addons.liza_payment_info.models.account_move.liza_send_open_invoices")
    def test_cron_skips_disabled_company(self, mock_send):
        self._set_credentials()
        self.company.liza_payment_info_enable = False
        self._create_open_invoice()
        self.env["account.move"]._cron_liza_send_open_invoices()
        mock_send.assert_not_called()

    @mute_logger("odoo.addons.liza_payment_info.models.account_move")
    @patch("odoo.addons.liza_payment_info.models.account_move.liza_send_open_invoices")
    def test_cron_skips_missing_credentials(self, mock_send):
        self.env["ir.config_parameter"].sudo().set_param("liza.payex.url", PAYEX_URL)
        self.company.liza_payment_info_enable = True
        self.company.liza_login = False
        self.company.liza_password = False
        self._create_open_invoice()
        self.env["account.move"]._cron_liza_send_open_invoices()
        mock_send.assert_not_called()

    @mute_logger("odoo.addons.liza_payment_info.models.account_move")
    @patch("odoo.addons.liza_payment_info.models.account_move.liza_send_open_invoices")
    def test_cron_skips_when_no_url(self, mock_send):
        self._set_credentials()
        # Clear the PayEx URL: the cron must return early
        self.env["ir.config_parameter"].sudo().set_param("liza.payex.url", "")
        self.company.liza_payment_info_enable = True
        self._create_open_invoice()
        self.env["account.move"]._cron_liza_send_open_invoices()
        mock_send.assert_not_called()

    @mute_logger("odoo.addons.liza_payment_info.models.account_move")
    @patch("odoo.addons.liza_payment_info.models.account_move.liza_send_open_invoices")
    def test_cron_skips_unsupported_supplier_country(self, mock_send):
        self._set_credentials()
        self.company.liza_payment_info_enable = True
        self.company.country_id = self.env.ref("base.uk").id
        self._create_open_invoice()
        self.env["account.move"]._cron_liza_send_open_invoices()
        mock_send.assert_not_called()

    @mute_logger("odoo.addons.liza_payment_info.models.account_move")
    @patch("odoo.addons.liza_payment_info.models.account_move.liza_send_open_invoices")
    def test_cron_skips_missing_supplier_identifier(self, mock_send):
        self._set_credentials()
        self.company.liza_payment_info_enable = True
        self.company.sudo().write({"company_registry": False, "vat": False})
        self._create_open_invoice()
        self.env["account.move"]._cron_liza_send_open_invoices()
        mock_send.assert_not_called()

    @mute_logger("odoo.addons.liza_payment_info.models.account_move")
    @patch("odoo.addons.liza_payment_info.models.account_move.liza_send_open_invoices")
    def test_cron_uses_supplier_vat_when_no_registry(self, mock_send):
        mock_send.return_value = (0, {})
        self._set_credentials()
        self.company.liza_payment_info_enable = True
        self.company.sudo().write({"company_registry": False, "vat": "BE0869703978"})
        self._create_open_invoice()
        self.env["account.move"]._cron_liza_send_open_invoices()
        mock_send.assert_called_once()
        self.assertEqual(
            mock_send.call_args.kwargs["supplier_identifier_type"], "VatNumber"
        )

    @mute_logger("odoo.addons.liza_payment_info.models.account_move")
    @patch("odoo.addons.liza_payment_info.models.account_move.liza_send_open_invoices")
    def test_cron_handles_api_error(self, mock_send):
        # A non-zero status must be handled (logged) without raising
        mock_send.return_value = (1, "Some API error")
        self._set_credentials()
        self.company.liza_payment_info_enable = True
        self._create_open_invoice()
        self.env["account.move"]._cron_liza_send_open_invoices()
        mock_send.assert_called_once()

    @patch("odoo.addons.liza_payment_info.liza_utils.liza_client")
    def test_send_open_invoices_returns_summary_on_success(self, mock_client):
        """A successful call hands back the invoice summary."""
        mock_client.return_value.service.SendOpenInvoices.return_value = {
            "StatusCode": 0,
            "InvoicesSummary": {"Accepted": 2},
        }
        status, result = liza_send_open_invoices(
            PAYEX_URL,
            "login",
            "password",
            "NL",
            "1.0",
            "BE",
            "RegistrationNumber",
            "0405056855",
            [],
        )
        self.assertEqual(status, 0)
        self.assertEqual(result, {"Accepted": 2})

    @patch("odoo.addons.liza_payment_info.liza_utils.liza_client")
    def test_send_open_invoices_returns_message_on_error(self, mock_client):
        """A refused call must return Liza's message rather than an empty
        summary that reads like a success."""
        mock_client.return_value.service.SendOpenInvoices.return_value = {
            "StatusCode": 101,
            "StatusMessage": "Invalid credentials",
            "InvoicesSummary": None,
        }
        status, result = liza_send_open_invoices(
            PAYEX_URL,
            "login",
            "password",
            "NL",
            "1.0",
            "BE",
            "RegistrationNumber",
            "0405056855",
            [],
        )
        self.assertEqual(status, 101)
        self.assertEqual(result, "Invalid credentials")
