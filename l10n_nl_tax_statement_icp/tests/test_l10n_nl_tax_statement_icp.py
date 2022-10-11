# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError, ValidationError

from odoo.addons.l10n_nl_tax_statement.tests.test_l10n_nl_vat_statement import (
    TestVatStatement,
)


class TestTaxStatementIcp(TestVatStatement):
    def _prepare_icp_invoice(self):

        self.invoice_1._post()
        for invoice_line in self.invoice_1.invoice_line_ids:
            invoice_line.tax_tag_ids = self.tag_5
        self.invoice_1._onchange_invoice_line_ids()
        self.statement_with_icp.statement_update()

    def test_02_no_tag_3b_omzet(self):
        self.statement_not_valid = self.env["l10n.nl.vat.statement"].create(
            {"name": "Statement 1"}
        )
        self.statement_not_valid.statement_update()
        with self.assertRaises(UserError):
            self.statement_not_valid.post()

    def test_03_post_final(self):
        self.statement_with_icp = self.env["l10n.nl.vat.statement"].create(
            {"name": "Statement 1"}
        )

        # all previous statements must be already posted
        self.statement_with_icp.statement_update()
        with self.assertRaises(UserError):
            self.statement_with_icp.post()

        self.statement_1.statement_update()
        self.statement_1.post()
        self.assertEqual(self.statement_1.state, "posted")

        # first post
        self.statement_with_icp.post()

        self.assertEqual(self.statement_with_icp.state, "posted")
        self.assertTrue(self.statement_with_icp.date_posted)

        self.statement_with_icp.icp_update()

        # then finalize
        self.statement_with_icp.finalize()
        self.assertEqual(self.statement_with_icp.state, "final")
        self.assertTrue(self.statement_with_icp.date_posted)

        with self.assertRaises(UserError):
            self.statement_with_icp.icp_update()

    def test_04_icp_invoice(self):
        self._create_test_invoice()
        self.invoice_1.partner_id.country_id = self.env.ref("base.be")
        self.statement_1.post()
        self.statement_with_icp = self.env["l10n.nl.vat.statement"].create(
            {"name": "Statement 1"}
        )

        self._prepare_icp_invoice()

        self.statement_with_icp.post()
        self.assertTrue(self.statement_with_icp.icp_line_ids)
        self.assertTrue(self.statement_with_icp.icp_total)

        for icp_line in self.statement_with_icp.icp_line_ids:
            self.assertTrue(icp_line.amount_products)
            self.assertFalse(icp_line.amount_services)
            amount_products = icp_line.format_amount_products
            self.assertEqual(float(amount_products), icp_line.amount_products)
            amount_services = icp_line.format_amount_services
            self.assertEqual(float(amount_services), icp_line.amount_services)

    def test_05_icp_invoice_service(self):
        self._create_test_invoice()
        self.statement_1.post()
        self.statement_with_icp = self.env["l10n.nl.vat.statement"].create(
            {"name": "Statement 1"}
        )

        self.invoice_1.partner_id.country_id = self.env.ref("base.be")
        self.invoice_1._post()
        for invoice_line in self.invoice_1.invoice_line_ids:
            invoice_line.tax_tag_ids = self.tag_6
        self.invoice_1._onchange_invoice_line_ids()
        self.statement_with_icp.statement_update()

        self.statement_with_icp.post()
        self.assertTrue(self.statement_with_icp.icp_line_ids)
        self.assertTrue(self.statement_with_icp.icp_total)

        for icp_line in self.statement_with_icp.icp_line_ids:
            self.assertFalse(icp_line.amount_products)
            self.assertTrue(icp_line.amount_services)
            amount_products = icp_line.format_amount_products
            self.assertEqual(float(amount_products), icp_line.amount_products)
            amount_services = icp_line.format_amount_services
            self.assertEqual(float(amount_services), icp_line.amount_services)

    def test_06_icp_invoice_nl(self):
        self._create_test_invoice()
        self.statement_1.post()
        self.statement_with_icp = self.env["l10n.nl.vat.statement"].create(
            {"name": "Statement 1"}
        )

        self.invoice_1.partner_id.country_id = self.env.ref("base.nl")
        self._prepare_icp_invoice()

        with self.assertRaises(ValidationError):
            self.statement_with_icp.post()

    def test_07_icp_invoice_outside_europe(self):
        self._create_test_invoice()
        self.statement_1.post()
        self.statement_with_icp = self.env["l10n.nl.vat.statement"].create(
            {"name": "Statement 1"}
        )

        self.invoice_1.partner_id.country_id = self.env.ref("base.us")
        self._prepare_icp_invoice()

        with self.assertRaises(ValidationError):
            self.statement_with_icp.post()
