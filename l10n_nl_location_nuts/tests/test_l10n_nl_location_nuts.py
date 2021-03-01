# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from os.path import dirname, join

from vcr import VCR

from odoo.tests.common import TransactionCase

from ..hooks import post_init_hook

logging.getLogger("vcr").setLevel(logging.WARNING)

recorder = VCR(
    record_mode="once",
    cassette_library_dir=join(dirname(__file__), "vcr_cassettes"),
    path_transformer=VCR.ensure_suffix(".yaml"),
    filter_headers=["Authorization"],
)


class TestNlLocationNuts(TransactionCase):
    def setUp(self):
        super().setUp()

        importer = self.env["nuts.import"]
        with recorder.use_cassette("nuts_import"):
            importer.run_import()

    def test_dutch_nuts(self):
        """
        Test that level 3 nuts correctly bind Dutch provinces.
        """
        self.nb_nuts = self.env["res.partner.nuts"].search([("code", "=", "NL41")])
        self.assertTrue(self.nb_nuts)
        self.assertTrue(self.nb_nuts.state_id)

        self.nl_partner = self.env["res.partner"].create(
            {"name": "Dutch Partner", "country_id": self.env.ref("base.nl").id}
        )
        self.nl_partner.state_id = self.nb_nuts.state_id

        # Onchange method binds level 3 nuts with Dutch provinces.
        self.nl_partner.onchange_state_id_base_location_nuts()
        self.assertEqual(self.nl_partner.state_id, self.nl_partner.nuts3_id.state_id)

    def test_post_init_hook(self):
        """
        Tests the post_init_hook.
        """
        base_nl = self.env.ref("base.nl")
        base_nl.state_level = False
        self.assertFalse(base_nl.state_level)
        post_init_hook(self.cr, self.env)
        self.assertEqual(base_nl.state_level, 3)
