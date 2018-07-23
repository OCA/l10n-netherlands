# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_nl_kvk_service = fields.Selection([
        ('test', 'Kamer van Koophandel (TEST)'),
        ('kvk', 'Kamer van Koophandel (KvK API)'),
    ], string='KvK API Service', required=True)
    l10n_nl_kvk_timeout = fields.Integer(required=True)
    l10n_nl_kvk_api_key = fields.Char()
    l10n_nl_kvk_api_value = fields.Char()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            l10n_nl_kvk_api_key=get_param('l10n_nl_kvk_api_key'),
            l10n_nl_kvk_api_value=get_param('l10n_nl_kvk_api_value'),
            l10n_nl_kvk_service=get_param('l10n_nl_kvk_service', 'test'),
            l10n_nl_kvk_timeout=int(get_param('l10n_nl_kvk_timeout', 3)),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param

        set_param('l10n_nl_kvk_api_key', self.l10n_nl_kvk_api_key)
        set_param('l10n_nl_kvk_api_value', self.l10n_nl_kvk_api_value)
        set_param('l10n_nl_kvk_service', self.l10n_nl_kvk_service)
        set_param('l10n_nl_kvk_timeout', self.l10n_nl_kvk_timeout)
