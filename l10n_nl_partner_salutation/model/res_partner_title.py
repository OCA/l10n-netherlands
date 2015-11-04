# -*- coding: utf-8 -*-
"""Extend res.partner.title model."""
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014-2015 Therp BV <http://therp.nl>.
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
from openerp import models, fields


class ResPartnerTitle(models.Model):
    """Extend res.partner.title model."""
    _inherit = 'res.partner.title'

    salutation = fields.Char(size=64, translate=True)
    salutation_male = fields.Char(string='Salutation male')
    salutation_female = fields.Char(string='Salutation female')
    shortcut_male = fields.Char(string='Shortcut male')
    shortcut_female = fields.Char(string='Shortcut female')
    postnominal = fields.Char(string='Postnominal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
