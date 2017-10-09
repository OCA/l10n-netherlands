# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestPartnerSalutation(TransactionCase):
    """Class test correct salutations for all genders and none."""

    post_install = True
    at_install = False

    def test_salutation_company(self):
        """Test that companies do not get salutation."""
        res_partner_model = self.env['res.partner']
        partner = res_partner_model.create({
            'is_company': True,
            'name': 'Best Washing machines Incorporated',
            'gender': False,  # Should be default, just make explicit
        })
        self.assertEqual(partner.salutation, False)
        self.assertEqual(partner.salutation_address, False)

    def test_salutation_male(self):
        """Test male salutation."""
        res_partner_model = self.env['res.partner']
        partner = res_partner_model.create({
            'is_company': False,
            'lastname': 'Anderson',
            'initials': 'Mr.',
            'infix': 'A.',
            'firstname': 'Thomas',
            'gender': 'male',
        })
        salutation_name = partner.get_salutation_name()
        self.assertEqual(
            partner.salutation,
            'Geachte heer %s' % salutation_name)
        self.assertEqual(
            partner.salutation_address,
            'De heer %s' % salutation_name)

    def test_salutation_female(self):
        """Test female salutation."""
        res_partner_model = self.env['res.partner']
        partner = res_partner_model.create({
            'is_company': False,
            'lastname': 'Anderson',
            'initials': 'Ms.',
            'infix': 'A.',
            'firstname': 'Maria',
            'gender': 'female',
        })
        salutation_name = partner.get_salutation_name()
        self.assertEqual(
            partner.salutation,
            'Geachte mevrouw %s' % salutation_name)
        self.assertEqual(
            partner.salutation_address,
            'Mevrouw %s' % salutation_name)

    def test_salutation_other(self):
        """Test other salutation."""
        res_partner_model = self.env['res.partner']
        partner = res_partner_model.create({
            'is_company': False,
            'lastname': 'Anderson',
            'initials': 'Ms.',
            'infix': 'A.',
            'firstname': 'Maria',
            'gender': 'other',
        })
        salutation_name = partner.get_salutation_name()
        self.assertEqual(partner.salutation, 'Geachte %s' % salutation_name)
        self.assertEqual(partner.salutation_address, salutation_name)

    def test_salutation_unknown(self):
        """Test unknown salutation."""
        res_partner_model = self.env['res.partner']
        partner = res_partner_model.create({
            'lastname': 'Anderson',
            'initials': 'Ms.',
            'infix': 'A.',
            'firstname': 'Maria',
            'gender': False,
        })
        salutation_name = partner.get_salutation_name()
        self.assertEqual(
            partner.salutation,
            'Geachte heer of mevrouw %s' % salutation_name)
        self.assertEqual(
            partner.salutation_address,
            'De heer of mevrouw %s' % salutation_name)
