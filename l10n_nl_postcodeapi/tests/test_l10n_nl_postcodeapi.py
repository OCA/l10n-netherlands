# Copyright 2018-2020 Onestein <https://www.onestein.eu>.
# Copyright 2021 Therp BV <https://therp.nll>.
# With inspiration from: https://realpython.com/testing-third-party-apis-with-mocks/
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Test the postcode api using a mock service."""
# pylint: disable=protected-access,unused-argument
from mock import patch

from pyPostcode import ResourceV2

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestPostcodeApi(SavepointCase):
    """Test the postcode api using a mock service."""

    @classmethod
    def setUpClass(cls):
        """Setup test."""
        super().setUpClass()
        # Get the pyPostcode.Api from the actual class where used.
        path_addon = 'odoo.addons.l10n_nl_postcodeapi.'
        path_file = 'models.ir_config_parameter.'
        cls.api_handler = path_addon + path_file
        cls.mock_getaddress_patcher = patch(
            cls.api_handler + 'pyPostcode.Api.getaddress'
        )
        cls.mock_getaddress = cls.mock_getaddress_patcher.start()
        cls.country_nl = cls.env.ref('base.nl')
        cls.config_parameter = cls.env.ref('l10n_nl_postcodeapi.parameter_apikey')
        # Make sure there is some value, in the key, otherwise api will not run.
        cls.config_parameter.write({'value': 'Some random value'})

    @classmethod
    def tearDownClass(cls):
        """Unpatch API."""
        cls.mock_getaddress = cls.mock_getaddress_patcher.stop()
        super().tearDownClass()

    def test_ir_config_parameter(self):
        """Test setting of configuration parameter."""
        # Verify l10n_nl_postcodeapi.apikey is created.
        self.assertTrue(self.config_parameter)
        # Setting apikey to invalid value should result in Exception.
        with self.assertRaises(UserError):
            self.mock_getaddress.return_value = False
            self.config_parameter.write({'value': 'KEYXXXXXXXXXXXNOTVALID'})

    def test_orm_cache(self):
        """Repeated calls to get_provider_obj should just return existing value."""
        self.mock_getaddress.return_value = ResourceV2(
            {
                "postcode": 'test 1053NJ',
                "house_number": '334T',
                "street": "Jacob van Lennepkade",
                "town": "Amsterdam",
                "province": {"id": 20, "label": "Noord-Holland"},
            }
        )
        parameter_model = self.env["ir.config_parameter"]
        parameter_model.get_provider_obj()
        saved_call_count = self.mock_getaddress.call_count
        # Call again...
        parameter_model.get_provider_obj()
        self.assertEqual(saved_call_count, self.mock_getaddress.call_count)
        # Writing new key should cause extra call.
        self.config_parameter.write({'value': 'Another random value'})
        self.assertEqual(
            1,
            self.mock_getaddress.call_count - saved_call_count
        )

    def test_res_partner_with_province(self):
        """Test setting partner with state/province."""
        # Create In Memory partner (no actual db update).
        partner = self.env['res.partner'].new({
            'name': 'test partner',
            'country_id': self.country_nl.id,
            'street_number': '10',
            'zip': 'test 4811DJ',
        })
        self.mock_getaddress.return_value = ResourceV2(
            {
                "postcode": 'test 4811DJ',
                "house_number": '10',
                "street": "Claudius Prinsenlaan",
                "town": "Breda",
                "province": {"id": 1, "label": "Noord-Brabant"},
            }
        )
        partner.on_change_zip_street_number()
        self.assertEqual(partner.street_name, 'Claudius Prinsenlaan')
        self.assertEqual(partner.city, 'Breda')
        self.assertEqual(partner.state_id.name, 'Noord-Brabant')
        self.assertEqual(partner.state_id.code, 'NL-NB')

    def test_res_partner_no_province(self):
        """Test setting partner with postalcode not linked to province.

        Province should not be filled. That is because we do not create a partner in
        the database, but only in memory. So the logic that assigns a province
        based on the ranges of zip-code for each province, part of the module
        l10n_nl_contry_states, is not called.
        """
        partner = self.env['res.partner'].new({
            'name': 'test partner',
            'country_id': self.country_nl.id,
            'street_number': '10',
            'state_id': False,
            'zip': '1018BC',
        })
        self.mock_getaddress.return_value = ResourceV2(
            {
                "postcode": '1018BC',
                "house_number": '10',
                "street": "Blankenstraat",
                "town": "Amsterdam",
                "province": False,
            }
        )
        partner.on_change_zip_street_number()
        self.assertEqual(partner.street_name, 'Blankenstraat')
        self.assertEqual(partner.city, 'Amsterdam')
        self.assertEqual(partner.state_id.name, False)

    def test_res_partner_incomplete_information(self):
        """Test on_change for partner in Netherlands without postalcode."""
        partner = self.env['res.partner'].new({
            'name': 'test partner',
            'country_id': self.country_nl.id,
            'street_number': '10',
        })
        self.mock_getaddress.return_value = False
        partner.on_change_zip_street_number()
        self.assertEqual(partner.street_number, '10')
        self.assertFalse(partner.street_name)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)

    def test_res_partner_other_country(self):
        """Test on_change for partner in another country."""
        country_it = self.env['res.country'].search([
            ('code', 'like', 'IT')
        ], limit=1)
        partner = self.env['res.partner'].new({
            'name': 'test partner',
            'country_id': country_it.id,
            'street_number': '10',
            'zip': '4811dj',
        })
        partner.on_change_zip_street_number()
        self.assertEqual(partner.street_number, '10')
        self.assertFalse(partner.street_name)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)

    def test_res_partner_no_key(self):
        """Test on_change while API key not set."""
        self.config_parameter.write({'value': 'Your API key'})
        partner = self.env['res.partner'].new({
            'name': 'test partner',
            'street_number': '10',
            'zip': '4811dj',
            'country_id': self.country_nl.id,
        })
        partner.on_change_zip_street_number()
        self.assertEqual(partner.street_number, '10')
        self.assertFalse(partner.street_name)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)

    def test_get_country_state(self):
        """Test get_country state with and without state_name."""
        state_brabant = self.env.ref("l10n_nl_country_states.state_noordbrabant")
        partner_model = self.env['res.partner']
        # Call with full information.
        state = partner_model.get_country_state(self.country_nl, "Noord-Brabant")
        self.assertTrue(bool(state))
        self.assertEqual(state.name, state_brabant.name)
        self.assertEqual(state.code, state_brabant.code)
        # Call with missing province should return empty recordset.
        state = partner_model.get_country_state(self.country_nl, False)
        self.assertFalse(bool(state))
        self.assertFalse(state.id)
