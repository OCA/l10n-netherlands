# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestL10nNlCountryStates(TransactionCase):
    def test_l10n_nl_country_states(self):
        partner = self.env['res.partner'].create({
            'name': 'Therp',
            'zip': '1053 NJ',
        })
        self.assertEqual(
            partner.state_id,
            self.env.ref('l10n_nl_country_states.state_noordholland'),
        )
        partner.write({'name': 'Therp BV'})
        partner.write({'contry_id': self.env.ref('base.be').id})
        self.assertEqual(
            partner.state_id,
            self.env.ref('l10n_nl_country_states.state_noordholland'),
        )
        partner.write({
            'contry_id': self.env.ref('base.nl').id,
            'zip': '9711LM',
        })
        self.assertEqual(
            partner.state_id,
            self.env.ref('l10n_nl_country_states.state_groningen'),
        )
