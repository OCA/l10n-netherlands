# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_nl_kvk_service = fields.Selection(selection_add=[
        ('openkvk', 'OpenKvK (gebruikt de Overheid.io API)'),
    ])

    l10n_nl_openkvk_api_value = fields.Char(
        config_parameter='l10n_nl_openkvk_api_value'
    )
