# Copyright 2017-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_nl_tax_invoice_basis = fields.Boolean(
        string="NL Tax Invoice Basis", default=True
    )
    l10n_nl_tax_statement_journal_id = fields.Many2one(
        comodel_name="account.journal",
        help="Journal used to post the journal entry for the NL VAT statement.",
    )
    l10n_nl_tax_statement_rounding_account_id = fields.Many2one(
        comodel_name="account.account",
        help=(
            "Account used to book the rounding difference of the "
            "NL VAT statement journal entry.",
        ),
    )
    l10n_nl_tax_statement_partner_id = fields.Many2one(
        comodel_name="res.partner",
        help=(
            "Partner used on the payable/receivable line of the NL VAT "
            "statement journal entry. Its payable/receivable account is "
            "used for that line."
        ),
    )
