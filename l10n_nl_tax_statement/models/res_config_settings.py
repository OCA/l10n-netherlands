# Copyright 2017-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_nl_tax_invoice_basis = fields.Boolean(
        string="NL Tax Invoice Basis",
        related="company_id.l10n_nl_tax_invoice_basis",
    )
