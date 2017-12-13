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

    firstname = fields.Char(related=['address_id', 'firstname'], store=False)
    lastname = fields.Char(related=['address_id', 'lastname'], store=False)
    initials = fields.Char(related=['address_id', 'initials'], store=False)
    infix = fields.Char(related=['address_id', 'infix'], store=False)

    # onchange_company, onchange_address_id, _reassign_user_id_partner 
    # in the module hr_employee_data_from_work_address work for this 
    # module too. I copy _register_hook for this module fields too.

    def _register_hook(self, cr):
        for field in ['firstname', 'lastname', 'initials', 'infix']:
            if field in self._columns:
                self._columns[field].store = False
                self._fields[field].column = self._columns[field]
            self._fields[field].store = False
            self.pool._store_function[self._name] = [
                spec
                for spec in self.pool._store_function[self._name]
                if spec[1] != field
            ]

    name_formal = fields.Char(
        string='Name', compute='_compute_display_name_formal', store=True)
    name_informal = fields.Char(
        string='Name', compute='_compute_display_name_formal', store=True)

    # computing NL stile formal and informal names
    @api.depends('initials', 'firstname', 'infix', 'name')
    @api.multi
    def _compute_display_name_formal(self):
        for employee in self:
            myname = ''
            informal = ''
            if employee.firstname:
                informal += employee.firstname + ' '
            if employee.initials:
                myname += employee.initials + ' '
            else:
                if employee.firstname:
                    myname += employee.firstname + ' '
            if employee.infix:
                myname += employee.infix + ' '
                informal += employee.infix + ' '
            if employee.name:
                myname += employee.name
                informal += employee.name
            employee.name_formal = myname.strip()
            employee.name_informal = informal.strip()

