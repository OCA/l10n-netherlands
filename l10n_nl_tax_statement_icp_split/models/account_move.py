# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_nl_icp_statement_id = fields.Many2one("l10n.nl.icp.statement")

    def write(self, vals):
        if (
            self.env.context.get("l10n_nl_icp_statement")
            and "l10n_nl_vat_statement_id" in vals
        ):
            vals["l10n_nl_icp_statement_id"] = vals.pop("l10n_nl_vat_statement_id")
        return super().write(vals)
