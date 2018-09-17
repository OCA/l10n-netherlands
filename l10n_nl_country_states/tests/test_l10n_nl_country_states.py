# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


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

    def test_dutch_country_states_noop(self):
        # Partner with Dutch province but other country
        n_brabant = self.env.ref('l10n_nl_country_states.state_noordbrabant')
        partner = self.env['res.partner'].create({
            'name': 'Onestein',
            'country_id': self.env.ref('base.be').id,
            'state_id': n_brabant.id,
            'zip': '4814 DC'})
        self.assertFalse(partner.state_id)

        partner.write({
            'zip': '4814 DC'})
        self.assertFalse(partner.state_id)

        # Partner with foreign province and country
        florida = self.env.ref('base.state_us_10')
        partner.write({
            'country_id': self.env.ref('base.us').id,
            'state_id': florida.id,
            'zip': '4814 DC'})
        self.assertEqual(partner.state_id, florida)

        partner.write({
            'zip': '4814 DC'})
        self.assertEqual(partner.state_id, florida)

    def test_onchange_zip(self):
        # Partner with country Netherlands and Dutch zip
        partner = self.env['res.partner'].create({
            'name': 'Any Company',
            'country_id': self.env.ref('base.nl').id,
            'zip': '1053 NJ'})
        self.assertEqual(
            partner.state_id,
            self.env.ref('l10n_nl_country_states.state_noordholland'))

        # Onchange zip, state should be updated
        partner.zip = '9711LM'
        partner.onchange_zip_country_id()
        self.assertEqual(
            partner.state_id,
            self.env.ref('l10n_nl_country_states.state_groningen'))

        # Onchange country to Belgium, state should be cleared
        partner.country_id = self.env.ref('base.be')
        partner.onchange_zip_country_id()
        self.assertFalse(partner.state_id)

        # Onchange country back to Netherlands, state should be set
        partner.country_id = self.env.ref('base.nl')
        partner.onchange_zip_country_id()
        self.assertEqual(
            partner.state_id,
            self.env.ref('l10n_nl_country_states.state_groningen'))
