# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import api, models

from odoo.addons.liza_base.liza_const import ALLOWED_COUNTRY_CODES

from ..liza_utils import liza_send_open_invoices

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _liza_prepare_invoice_values(self):
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id
        customer_country_code = partner.country_id.code
        if customer_country_code not in ALLOWED_COUNTRY_CODES:
            return None
        if partner.company_registry:
            identifier_type = "RegistrationNumber"
            identifier = partner.company_registry
        elif partner.vat:
            identifier_type = "VatNumber"
            identifier = partner.vat
        else:
            return None
        return {
            "InvoiceNumber": self.name,
            "InvoiceDate": self.invoice_date.strftime("%Y%m%d"),
            "OpenAmountWhole": str(int(self.amount_residual)),
            "CustomerCountry": customer_country_code,
            "CustomerIdentifierType": identifier_type,
            "CustomerIdentifier": identifier,
        }

    @api.model
    def _cron_liza_send_open_invoices(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        url = IrConfigParameter.get_param("liza.payex.url", "")
        if not url:
            _logger.warning("Liza: No PayEx URL configured (liza.payex.url), skipping.")
            self.env["ir.logging"].sudo().create(
                {
                    "name": _logger.name,
                    "type": "server",
                    "level": "WARNING",
                    "message": (
                        "Liza: No PayEx URL configured (liza.payex.url), skipping."
                    ),
                    "path": __name__,
                    "func": "_cron_liza_send_open_invoices",
                    "line": 0,
                }
            )
            return

        module = (
            self.env["ir.module.module"]
            .sudo()
            .search([("name", "=", "liza_payment_info")], limit=1)
        )
        package_version = module.installed_version

        for company in self.env["res.company"].sudo().search([]):  # pylint: disable=no-search-all
            if not company.liza_payment_info_enable:
                continue
            if not company.liza_login or not company.liza_password:
                _logger.warning(
                    "Liza: Missing credentials for company %s, skipping.",
                    company.name,
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "WARNING",
                        "message": (
                            f"Liza: Missing credentials for company"
                            f" {company.name}, skipping."
                        ),
                        "path": __name__,
                        "func": "_cron_liza_send_open_invoices",
                        "line": 0,
                    }
                )
                continue

            supplier_country_code = company.country_id.code
            if supplier_country_code not in ALLOWED_COUNTRY_CODES:
                _logger.warning(
                    "Liza: Unsupported supplier country %s for company %s.",
                    supplier_country_code,
                    company.name,
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "WARNING",
                        "message": (
                            f"Liza: Unsupported supplier country"
                            f" {supplier_country_code} for company {company.name}."
                        ),
                        "path": __name__,
                        "func": "_cron_liza_send_open_invoices",
                        "line": 0,
                    }
                )
                continue

            if company.company_registry:
                supplier_identifier_type = "RegistrationNumber"
                supplier_identifier = company.company_registry
            elif company.vat:
                supplier_identifier_type = "VatNumber"
                supplier_identifier = company.vat
            else:
                _logger.warning(
                    "Liza: No VAT or registry number for company %s, skipping.",
                    company.name,
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "WARNING",
                        "message": (
                            f"Liza: No VAT or registry number"
                            f" for company {company.name}, skipping."
                        ),
                        "path": __name__,
                        "func": "_cron_liza_send_open_invoices",
                        "line": 0,
                    }
                )
                continue

            open_invoices = self.search(
                [
                    ("move_type", "=", "out_invoice"),
                    ("state", "=", "posted"),
                    ("payment_state", "in", ("not_paid", "partial")),
                    ("company_id", "=", company.id),
                ]
            )

            invoices_list = []
            for move in open_invoices:
                vals = move._liza_prepare_invoice_values()
                if vals:
                    invoices_list.append(vals)

            if not invoices_list:
                _logger.info(
                    "Liza: No eligible open invoices for company %s.",
                    company.name,
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "INFO",
                        "message": (
                            f"Liza: No eligible open invoices"
                            f" for company {company.name}."
                        ),
                        "path": __name__,
                        "func": "_cron_liza_send_open_invoices",
                        "line": 0,
                    }
                )
                continue

            company_lang = (company.partner_id.lang or "en_US")[:2].upper()
            if company_lang not in ("FR", "NL"):
                company_lang = "EN"

            status, result = liza_send_open_invoices(
                url=url,
                login=company.liza_login,
                password=company.liza_password,
                lang=company_lang,
                package_version=package_version,
                supplier_country=supplier_country_code,
                supplier_identifier_type=supplier_identifier_type,
                supplier_identifier=supplier_identifier,
                invoices_list=invoices_list,
            )
            if status != 0:
                _logger.warning(
                    "Liza: Error %i sending open invoices for company %s: %s",
                    status,
                    company.name,
                    result,
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "WARNING",
                        "message": (
                            f"Liza: Error {status} sending"
                            f" open invoices for company {company.name}: {result}"
                        ),
                        "path": __name__,
                        "func": "_cron_liza_send_open_invoices",
                        "line": 0,
                    }
                )
            else:
                summary = result or {}
                _logger.info(
                    "Liza: Open invoices sent for company %s — "
                    "valid: %i, invalid: %i, unique customers: %i, "
                    "total open amount: %s",
                    company.name,
                    summary.get("NumberOfValidInvoices", 0),
                    summary.get("NumberOfInvalidInvoices", 0),
                    summary.get("NumberOfUniqueCustomers", 0),
                    summary.get("TotalOpenAmountOfValidInvoices", 0),
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "INFO",
                        "message": (
                            f"Liza: Open invoices sent for"
                            f" company {company.name} — "
                            f"valid: {summary.get('NumberOfValidInvoices', 0)}, "
                            f"invalid: {summary.get('NumberOfInvalidInvoices', 0)}, "
                            f"unique customers:"
                            f" {summary.get('NumberOfUniqueCustomers', 0)}, "
                            f"total open amount:"
                            f" {summary.get('TotalOpenAmountOfValidInvoices', 0)}"
                        ),
                        "path": __name__,
                        "func": "_cron_liza_send_open_invoices",
                        "line": 0,
                    }
                )
