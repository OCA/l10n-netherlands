# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_nl_kvk_service = fields.Selection(selection_add=[
        ('openkvk', 'OpenKvK (gebruikt de Overheid.io API)'),
    ])

    l10n_nl_openkvk_api_value = fields.Char()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            l10n_nl_openkvk_api_value=get_param('l10n_nl_openkvk_api_value'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param

        set_param('l10n_nl_openkvk_api_value', self.l10n_nl_openkvk_api_value)
