# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013-2015 Therp BV (<http://therp.nl>).
#
#    @autors: Stefan Rijnhart, Ronald Portier
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    @api.returns('self', lambda value: value.id)
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
