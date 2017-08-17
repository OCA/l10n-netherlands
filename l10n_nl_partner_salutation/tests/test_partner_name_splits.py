# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestPartnerNameSplits(TransactionCase):

    post_install = True
    at_install = False

    def test_splits(self):
        res_partner_model = self.env['res.partner']
        partner_male = res_partner_model.create({'lastname': 'Anderson',
                                                 'initials': 'Mr.',
                                                 'infix': 'A.',
                                                 'firstname': 'Thomas',
                                                 'gender': 'male'})
        partner_female = res_partner_model.create({'lastname': 'Anderson',
                                                   'initials': 'Ms.',
                                                   'infix': 'A.',
                                                   'firstname': 'Maria',
                                                   'gender': 'female'})
        partner_unknown = res_partner_model.create({'lastname': 'Anderson',
                                                    'initials': 'Ms.',
                                                    'infix': 'A.',
                                                    'firstname': 'Maria',
                                                    'gender': 'unknown'})
        self.assertEqual(partner_male.salutation,
                         'Geachte heer ' +
                         partner_male.firstname +
                         ' ' +
                         partner_male.infix +
                         ' ' +
                         partner_male.lastname)
        self.assertEqual(partner_male.salutation_address,
                         'De heer ' +
                         partner_male.firstname +
                         ' ' +
                         partner_male.infix +
                         ' ' +
                         partner_male.lastname)

        self.assertEqual(partner_female.salutation,
                         'Geachte mevrouw ' +
                         partner_female.firstname +
                         ' ' +
                         partner_female.infix +
                         ' ' +
                         partner_female.lastname)
        self.assertEqual(partner_female.salutation_address,
                         'Mevrouw ' +
                         partner_female.firstname +
                         ' ' +
                         partner_female.infix +
                         ' ' +
                         partner_female.lastname)

        self.assertEqual(partner_unknown.salutation,
                         'Geachte heer of mevrouw ' +
                         partner_unknown.firstname +
                         ' ' +
                         partner_unknown.infix +
                         ' ' +
                         partner_unknown.lastname)
        self.assertEqual(partner_unknown.salutation_address,
                         'De heer of mevrouw ' +
                         partner_unknown.firstname +
                         ' ' +
                         partner_unknown.infix +
                         ' ' +
                         partner_unknown.lastname)
