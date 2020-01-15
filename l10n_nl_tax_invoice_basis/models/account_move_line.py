# Copyright 2017-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_nl_date_invoice = fields.Date(
        compute="_compute_l10n_nl_date_invoice", store=True
    )

    @api.depends(
        "move_id",
        "move_id.invoice_date",
        "move_id.type",
        "company_id",
        "company_id.l10n_nl_tax_invoice_basis",
        "company_id.country_id",
    )
    def _compute_l10n_nl_date_invoice(self):
        for line in self:
            if line.parent_state == "draft" or not line.l10n_nl_date_invoice:
                company = line.move_id.company_id
                is_invoice_basis = company.l10n_nl_tax_invoice_basis
                is_nl = company.country_id == self.env.ref("base.nl")
                is_invoice = line.move_id.is_invoice(include_receipts=True)
                if is_invoice_basis and is_nl and is_invoice:
                    line.l10n_nl_date_invoice = line.move_id.invoice_date
            line.l10n_nl_date_invoice = line.l10n_nl_date_invoice
