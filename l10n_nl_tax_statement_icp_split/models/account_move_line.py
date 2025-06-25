# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_nl_icp_statement_id = fields.Many2one(
        related="move_id.l10n_nl_icp_statement_id", store=True
    )
