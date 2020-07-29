# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from odoo.modules.module import get_module_resource
from odoo.tests.common import TransactionCase


class TestNlPostcodeapi(TransactionCase):

    def setUp(self):
        super(TestNlPostcodeapi, self).setUp()

        # this block of code removes the existing provinces
        # eventually already created by module l10n_nl_country_states
        # to avoid conflicts with tests of l10n_nl_country_states
        is_l10n_nl_country_states_installed = self.env['ir.model']._get(
            'res.country.state.nl.zip'
        )
        self.country_nl = self.env['res.country'].search([
            ('code', 'like', 'NL')
        ], limit=1)
        self.assertTrue(self.country_nl)
        if is_l10n_nl_country_states_installed:
            NlZipStateModel = self.env['res.country.state.nl.zip']
            NlZipStateModel.search([]).unlink()
            states = self.env['res.country.state'].search([
                ('country_id', '=', self.country_nl.id)
            ])
            states.unlink()
        states = self.env['res.country.state'].search([
            ('country_id', '=', self.country_nl.id)
        ])
        states.unlink()

    def load_nl_provinces(self):
        csv_resource = get_module_resource(
            'l10n_nl_postcodeapi',
            'examples',
            'res.country.state.csv',
        )
        csv_file = open(csv_resource, 'rb').read()
        import_wizard = self.env['base_import.import'].create({
            'res_model': 'res.country.state',
            'file': csv_file,
            'file_type': 'text/csv'
        })

        result = import_wizard.parse_preview({
            'quoting': '"',
            'separator': ',',
            'headers': True,
        })
        self.assertIsNone(result.get('error'))
        results = import_wizard.do(
            ['id', 'country_id', 'name', 'code'],
            {'headers': True, 'separator': ',', 'quoting': '"'})
        self.assertFalse(
            results, "results should be empty on successful import")

    def test_01_ir_config_parameter(self):
        config_parameter = self.env['ir.config_parameter'].search([
            ('key', '=', 'l10n_nl_postcodeapi.apikey')
        ])
        # Verify l10n_nl_postcodeapi.apikey is created
        self.assertTrue(config_parameter)
        self.assertEqual(config_parameter.value, 'Your API key')

        # Verify l10n_nl_postcodeapi.apikey is modified
        config_parameter.write({
            'value': 'KEYXXXXXXXXXXXNOTVALID'
        })
        self.assertEqual(config_parameter.value, 'KEYXXXXXXXXXXXNOTVALID')

    def test_02_res_country_state(self):

        # Load res.country.state.csv
        self.load_nl_provinces()

        # Verify res.country.state created
        states = self.env['res.country.state'].search([
            ('country_id', '=', self.country_nl.id)
        ])
        self.assertTrue(states)

        # Verify res.country.state modified
        states[0].write({
            'name': 'test'
        })
        self.assertEqual(states[0].name, 'test')

        # Verify res.country.state unlinked
        states[0].unlink()
        test_states = self.env['res.country.state'].search([
            ('name', 'like', 'test')
        ])
        self.assertFalse(test_states)

    def test_03_res_partner_with_province(self):
        # Set l10n_nl_postcodeapi.apikey
        config_parameter = self.env['ir.config_parameter'].search([
            ('key', '=', 'l10n_nl_postcodeapi.apikey')
        ])
        config_parameter.write({
            'value': 'DZyipS65BT6n52jQHpVXs53r4bYK8yng3QWQT2tV'
        })

        def _patched_api_connector(*args, **kwargs):
            return False

        def _patched_api_get_address(*args, **kwargs):
            address = {
                "_data": "test",
                "street": "Claudius Prinsenlaan",
                "town": "Breda",
                "province": "Noord-Brabant"
            }
            return type('Address', tuple(), address)()

        patch_api_connector = patch(
            'odoo.addons.l10n_nl_postcodeapi.models.res_partner.ResPartner.'
            '_postcodeapi_check_valid_provider', _patched_api_connector)
        patch_api_get_address = patch(
            'pyPostcode.Api.getaddress', _patched_api_get_address)
        patch_api_connector.start()
        patch_api_get_address.start()

        # Load res.country.state.csv
        self.load_nl_provinces()

        partner = self.env['res.partner'].create({
            'name': 'test partner',
            'country_id': self.country_nl.id,
            'street_number': '10',
            'zip': 'test 4811dj',
        })
        res = partner.on_change_zip_street_number()
        self.assertFalse(res)

        patch_api_get_address.stop()
        patch_api_connector.stop()

        partner._convert_to_write(partner._cache)
        self.assertEqual(partner.street_name, 'Claudius Prinsenlaan')
        self.assertEqual(partner.city, 'Breda')
        self.assertEqual(partner.state_id.name, 'Noord-Brabant')
        self.assertEqual(partner.state_id.code, 'NB')
        self.assertEqual(partner.street, 'Claudius Prinsenlaan 10')

    def test_04_res_partner_no_province(self):
        # Set l10n_nl_postcodeapi.apikey
        config_parameter = self.env['ir.config_parameter'].search([
            ('key', '=', 'l10n_nl_postcodeapi.apikey')
        ])
        config_parameter.write({
            'value': 'DZyipS65BT6n52jQHpVXs53r4bYK8yng3QWQT2tV'
        })

        def _patched_api_connector(*args, **kwargs):
            return False

        def _patched_api_get_address(*args, **kwargs):
            address = {
                "_data": "test",
                "street": "Claudius Prinsenlaan",
                "town": "Breda",
                "province": "Noord-Brabant"
            }
            return type('Address', tuple(), address)()

        patch_api_connector = patch(
            'odoo.addons.l10n_nl_postcodeapi.models.res_partner.ResPartner.'
            '_postcodeapi_check_valid_provider', _patched_api_connector)
        patch_api_get_address = patch(
            'pyPostcode.Api.getaddress', _patched_api_get_address)
        patch_api_connector.start()
        patch_api_get_address.start()

        partner = self.env['res.partner'].create({
            'name': 'test partner',
            'country_id': self.country_nl.id,
            'street_number': '10',
            'zip': '4811dj',
        })
        res = partner.on_change_zip_street_number()
        self.assertFalse(res)

        patch_api_get_address.stop()
        patch_api_connector.stop()

        partner._convert_to_write(partner._cache)
        self.assertEqual(partner.street_name, 'Claudius Prinsenlaan')
        self.assertEqual(partner.city, 'Breda')
        self.assertFalse(partner.state_id)
        self.assertEqual(partner.street, 'Claudius Prinsenlaan 10')

    def test_05_res_partner_other_country(self):
        country_it = self.env['res.country'].search([
            ('code', 'like', 'IT')
        ], limit=1)
        partner = self.env['res.partner'].create({
            'name': 'test partner',
            'country_id': country_it.id,
            'street_number': '10',
            'zip': '4811dj',
        })
        res = partner.on_change_zip_street_number()
        self.assertFalse(res)
        partner._convert_to_write(partner._cache)
        self.assertFalse(partner.street_name)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)
        self.assertEqual(partner.street, '10')

    def test_06_res_partner_no_key(self):

        partner = self.env['res.partner'].create({
            'name': 'test partner',
            'street_number': '10',
            'zip': '4811dj',
            'country_id': self.country_nl.id,
        })
        res = partner.on_change_zip_street_number()
        self.assertFalse(res)
        partner._convert_to_write(partner._cache)
        self.assertFalse(partner.street_name)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)
