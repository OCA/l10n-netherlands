# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from ..hooks import post_init_hook


class TestNlLocationNuts(TransactionCase):

    def setUp(self):
        super().setUp()

        if not self.env['res.country.state'].search([
            ('code', "=", 'NB'),
            ('country_id', "=", self.env.ref('base.nl').id),
        ]):
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

    def test_post_init_hook(self):
        """
        Tests the post_init_hook.
        """
        base_nl = self.env.ref('base.nl')
        base_nl.state_level = False
        self.assertFalse(base_nl.state_level)
        post_init_hook(self.cr, self.env)
        self.assertEqual(base_nl.state_level, 3)
