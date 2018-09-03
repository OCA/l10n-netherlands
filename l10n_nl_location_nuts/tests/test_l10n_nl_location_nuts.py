# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestNlLocationNuts(TransactionCase):

    def setUp(self):
        super(TestNlLocationNuts, self).setUp()

        self.env['res.country.state'].create({
            'name': 'Noord-Brabant',
            'code': 'NB',
            'country_id': self.env.ref('base.nl').id
        })

        importer = self.env['nuts.import']
        importer.run_import()

    def test_dutch_nuts(self):
        """
        Test that level 3 nuts correctly bind Dutch provinces.
        """
        self.nb_nuts = self.env['res.partner.nuts'].search(
            [('code', '=', 'NL41')])
        self.assertTrue(self.nb_nuts)
        self.assertTrue(self.nb_nuts.state_id)

        self.nl_partner = self.env['res.partner'].create({
            'name': 'Dutch Partner',
            'country_id': self.env.ref('base.nl').id
        })
        self.nl_partner.state_id = self.nb_nuts.state_id

        # Onchange method binds level 3 nuts with Dutch provinces.
        self.nl_partner.onchange_state_id_base_location_nuts()
        self.assertEqual(
            self.nl_partner.state_id,
            self.nl_partner.nuts3_id.state_id)
