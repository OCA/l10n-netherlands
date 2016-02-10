# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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

from openerp.osv import orm


class IrConfigParameter(orm.Model):
    _inherit = 'ir.config_parameter'

    def create(self, cr, uid, vals, context=None):
        """
        Clear the postcode provider cache when the API
        key is created
        """
        if vals.get('key') == 'l10n_nl_postcodeapi.apikey':
            partner_obj = self.pool.get('res.partner')
            partner_obj.get_provider_obj.clear_cache(partner_obj)
        return super(IrConfigParameter, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        Clear the postcode provider cache when the API
        key is modified
        """
        key = 'l10n_nl_postcodeapi.apikey'
        clear = False
        if vals.get('key') == key:
            clear = True
        else:
            if ids and isinstance(ids, (int, long)):
                ids = [ids]
            if self.search(
                    cr, uid, [('id', 'in', ids), ('key', '=', key)],
                    context=context):
                clear = True
        if clear:
            partner_obj = self.pool.get('res.partner')
            partner_obj.get_provider_obj.clear_cache(partner_obj)
        return super(IrConfigParameter, self).write(
            cr, uid, ids, vals, context=context)
