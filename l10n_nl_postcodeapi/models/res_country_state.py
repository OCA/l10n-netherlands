# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013-2015 Therp BV (<http://therp.nl>).
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


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    @api.multi
    def write(self, vals):
        """
        Clear the postcode provider cache when the state
        table is altered.
        """
        self.env['res.partner'].get_province.clear_cache(
            self.env['res.partner'])
        return super(ResCountryState, self).write(vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        """
        Clear the postcode provider cache when the state
        table is altered.
        """
        self.env['res.partner'].get_province.clear_cache(
            self.env['res.partner'])
        return super(ResCountryState, self).create(vals)

    @api.multi
    def unlink(self):
        """
        Clear the postcode provider cache when the state
        table is altered.
        """
        self.env['res.partner'].get_province.clear_cache(
            self.env['res.partner'])
        return super(ResCountryState, self).unlink()
