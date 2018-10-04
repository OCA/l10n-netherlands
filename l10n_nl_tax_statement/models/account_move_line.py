# Copyright 2017-2018 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_nl_vat_statement_id = fields.Many2one(
        related='move_id.l10n_nl_vat_statement_id',
        store=True,
        readonly=True,
        string='Related Move Statement'
    )
    l10n_nl_vat_statement_include = fields.Boolean(
        related='move_id.l10n_nl_vat_statement_include',
        store=True,
        readonly=True
    )
