# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestDutchCountryStates(TransactionCase):
    def test_dutch_country_states(self):
        # Partner withouth country by default Dutch
        partner = self.env['res.partner'].create({
            'name': 'Therp',
            'zip': '1053 NJ'})
        self.assertEqual(
            partner.state_id,
            self.env.ref('l10n_nl_country_states.state_noordholland'))
        # When moving partner to Belgium, state should be cleared
        partner.write({
            'name': 'Therp BV',
            'country_id': self.env.ref('base.be').id})
        self.assertEqual(partner.state_id.id, False)  # compare with id!
        # Now move partner back to Netherlands/Groningen
        partner.write({
            'country_id': self.env.ref('base.nl').id,
            'zip': '9711LM'})
        self.assertEqual(
            partner.state_id,
            self.env.ref('l10n_nl_country_states.state_groningen'))
