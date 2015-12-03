# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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


class ResCountryState(orm.Model):
    _inherit = 'res.country.state'

    def write(self, cr, uid, ids, vals, context=None):
        """
        Clear the postcode provider cache when the state
        table is altered.
        """
        partner_obj = self.pool.get('res.partner')
        partner_obj.get_province.clear_cache(partner_obj)
        return super(ResCountryState, self).write(
            cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        """
        Clear the postcode provider cache when the state
        table is altered.
        """
        partner_obj = self.pool.get('res.partner')
        partner_obj.get_province.clear_cache(partner_obj)
        return super(ResCountryState, self).create(
            cr, uid, vals, context=context)
