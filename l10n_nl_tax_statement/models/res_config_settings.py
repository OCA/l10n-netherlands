# Copyright 2017-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_nl_tax_invoice_basis = fields.Boolean(
        string="NL Tax Invoice Basis",
        related="company_id.l10n_nl_tax_invoice_basis",
        readonly=False,
    )
    l10n_nl_tax_statement_journal_id = fields.Many2one(
        comodel_name="account.journal",
        related="company_id.l10n_nl_tax_statement_journal_id",
        readonly=False,
    )
    l10n_nl_tax_statement_rounding_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.l10n_nl_tax_statement_rounding_account_id",
        readonly=False,
    )
    l10n_nl_tax_statement_partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="company_id.l10n_nl_tax_statement_partner_id",
        readonly=False,
    )
