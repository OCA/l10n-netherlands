# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestL10nNlPartnerName(TransactionCase):
    def test_l10n_nl_hr_employee_name(self):
        # we create a employee
        employee = self.env['hr.employee'].create({
            'name': 'Mark Rutte',
        })
        # partner_firstname still works
        partner = self.env['res.partner'].create({
            'name': 'Mark Rutte',
        })
        employee = self.env['hr.employee'].create({
            'name': 'stephanie bergman'
            'address_id': partner.id
        })
        self.assertEqual(partner.firstname, 'Mark')
        self.assertEqual(partner.lastname, 'Rutte')
        self.assertEqual(employee2.firstname, 'stephanie')
        self.assertEqual(employee2.lastname, 'bergman')
