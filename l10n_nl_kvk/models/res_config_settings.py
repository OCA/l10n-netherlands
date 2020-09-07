# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_nl_kvk_service = fields.Selection([
        ('test', 'Kamer van Koophandel (TEST)'),
        ('kvk', 'Kamer van Koophandel (KvK API)'), ],
        default='test',
        string='KvK API Service',
        required=True,
        config_parameter='l10n_nl_kvk_service',
    )
    l10n_nl_kvk_timeout = fields.Integer(
        config_parameter='l10n_nl_kvk_timeout',
        default=3,
        required=True,
    )
    l10n_nl_kvk_api_key = fields.Char(
        config_parameter='l10n_nl_kvk_api_key',
    )
    l10n_nl_kvk_api_value = fields.Char(
        config_parameter='l10n_nl_kvk_api_value',
    )
