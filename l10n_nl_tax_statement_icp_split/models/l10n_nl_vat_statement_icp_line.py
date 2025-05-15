# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class L10nNlVatStatementIcpLine(models.Model):
    _inherit = "l10n.nl.vat.statement.icp.line"

    partner_id = fields.Many2one(required=False)
    icp_statement_id = fields.Many2one("l10n.nl.icp.statement", ondelete="cascade")
    error = fields.Text()
    move_line_ids = fields.Json()

    def _check_country_code(self):
        # remove the constraint
        return super()._check_country_code()

    def view_tax_lines(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_account_moves_all_tree"
        )
        action["context"] = {}
        action["domain"] = [
            ("id", "in", sum(filter(None, self.mapped("move_line_ids")), []))
        ]
        return action
