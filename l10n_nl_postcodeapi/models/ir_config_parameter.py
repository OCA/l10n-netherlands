# Copyright 2013-2015 Therp BV <https://therp.nl>
# @autors: Stefan Rijnhart, Ronald Portier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def create(self, vals):
        """
        Clear the postcode provider cache when the API
        key is created
        """
        if vals.get('key') == 'l10n_nl_postcodeapi.apikey':
            partner_obj = self.env['res.partner']
            partner_obj.get_provider_obj.clear_cache(partner_obj)
        return super(IrConfigParameter, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        Clear the postcode provider cache when the API
        key is modified
        """
        key = 'l10n_nl_postcodeapi.apikey'
        if (vals.get('key') == key or
                self.search([('id', 'in', self.ids), ('key', '=', key)])):
            partner_obj = self.env['res.partner']
            partner_obj.get_provider_obj.clear_cache(partner_obj)
        return super(IrConfigParameter, self).write(vals)
