# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class L10nNlVatStatementLine(models.Model):
    _inherit = "l10n.nl.vat.statement.line"

    icp_statement_id = fields.Many2one("l10n.nl.icp.statement", ondelete="cascade")
