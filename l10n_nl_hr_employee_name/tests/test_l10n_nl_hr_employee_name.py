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
        self.assertEqual(employee.firstname, 'Mark')
        self.assertEqual(employee.lastname, 'Rutte')
        employee.firstname = 'Willem-Alexander'
        employee.lastname = 'van Oranje-Nassau'
        self.assertEqual(
            employee.name,
            'Willem-Alexander van Oranje-Nassau'
        )
        
        employee.write({
            'name': employee.name,
        })
        self.assertEqual(employee.firstname, 'Willem-Alexander')
        self.assertEqual(employee.lastname, 'van Oranje-Nassau')


        partner = self.env['res.partner'].create({
            'name': 'Mark Rutte',
        })
        employee2 = self.env['hr.employee'].create({
            'name': 'should beReplaced'
            'address_id': partner.id
        })

        self.assertEqual(partner.firstname, 'Mark')
        self.assertEqual(partner.lastname, 'Rutte')
        self.assertEqual(employee2.firstname, 'Mark')
        self.assertEqual(employee2.lastname, 'Rutte')
