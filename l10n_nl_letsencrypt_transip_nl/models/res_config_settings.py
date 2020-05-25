# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    letsencrypt_dns_provider = fields.Selection(
        selection_add=[('transip', 'TransIP')],
    )
    letsencrypt_transip_login = fields.Char()
    letsencrypt_transip_key = fields.Text()

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        ir_config_parameter = self.env['ir.config_parameter']
        res.update({
            'letsencrypt_transip_login': ir_config_parameter.get_param(
                'letsencrypt_transip_login'),
            'letsencrypt_transip_key': ir_config_parameter.get_param(
                'letsencrypt_transip_key'),
        })
        return res

    @api.multi
    def set_values(self):
        super().set_values()

        ir_config_parameter = self.env['ir.config_parameter']
        ir_config_parameter.set_param(
            'letsencrypt_transip_login',
            self.letsencrypt_transip_login,
        )
        ir_config_parameter.set_param(
            'letsencrypt_transip_key',
            self.letsencrypt_transip_key,
        )
        return True
