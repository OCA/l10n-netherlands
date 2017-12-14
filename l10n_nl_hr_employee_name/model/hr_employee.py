# -*- coding: utf-8 -*-
"""Extend res.partner with extra fields for Dutch names."""
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013-2015 Therp BV <http://therp.nl>.
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
from mako.template import Template
from openerp import models, fields, api


class HrEmployee(models.Model):
    """Extend hr.employee with extra fields for Dutch names. Reusing the
    firstname, lastname, initials and infix from  partner_firstname and
    l10n_nl_partner_name, simpler and more consistent than repeating the logic
    """
    _inherit = 'hr.employee'

    firstname = fields.Char(string='firstname')
    lastname = fields.Char(string='lastname')
    initials = fields.Char(string='initials')
    infix = fields.Char(string='infix')
    calling_name = fields.Char(string='nickname')
