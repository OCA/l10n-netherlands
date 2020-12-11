# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from types import SimpleNamespace
from unittest.mock import Mock, patch

from odoo.modules.module import get_resource_path
from odoo.tests.common import TransactionCase


class TestNlPostcodeapi(TransactionCase):

    def setUp(self):
        super().setUp()

        # this block of code removes the existing provinces
        # eventually already created by module l10n_nl_country_states
        # to avoid conflicts with tests of l10n_nl_country_states
        # (note: not currently ported to 12.0)
        is_l10n_nl_country_states_installed = self.env['ir.model']._get(
            'res.country.state.nl.zip'
        )
        self.country_nl = self.get_country("NL")
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
        csv_resource = get_resource_path(
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
            [],
            {'headers': True, 'separator': ',', 'quoting': '"'}
        )["messages"]
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
        self.configure_key()

        # Load res.country.state.csv
        self.load_nl_provinces()

        partner = self.create_partner()
        with self.patch_api_get_address():
            partner.on_change_zip_street_number()

        partner._convert_to_write(partner._cache)
        self.assertEqual(partner.street_name, 'Claudius Prinsenlaan')
        self.assertEqual(partner.city, 'Breda')
        self.assertEqual(partner.state_id.name, 'Noord-Brabant')
        self.assertEqual(partner.state_id.code, 'NB')
        self.assertEqual(partner.street, 'Claudius Prinsenlaan 10')

    def test_04_res_partner_no_province(self):
        self.configure_key()

        partner = self.create_partner()
        with self.patch_api_get_address():
            partner.on_change_zip_street_number()

        partner._convert_to_write(partner._cache)
        self.assertEqual(partner.street_name, 'Claudius Prinsenlaan')
        self.assertEqual(partner.city, 'Breda')
        self.assertFalse(partner.state_id)
        self.assertEqual(partner.street, 'Claudius Prinsenlaan 10')

    def test_05_res_partner_other_country(self):
        self.configure_key()

        partner = self.create_partner(country="IT")
        with self.patch_api_get_address() as getaddr:
            partner.on_change_zip_street_number()
        getaddr.assert_not_called()

        partner._convert_to_write(partner._cache)
        self.assertFalse(partner.street_name)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)
        self.assertEqual(partner.street, '10')

    def test_06_res_partner_no_key(self):
        partner = self.create_partner()
        with self.patch_api_get_address() as getaddr:
            partner.on_change_zip_street_number()
        getaddr.assert_not_called()

        partner._convert_to_write(partner._cache)
        self.assertFalse(partner.street_name)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)

    def test_07_res_partner_no_result(self):
        self.configure_key()

        partner = self.create_partner()
        with self.patch_api_get_address() as getaddr:
            getaddr.return_value = False
            partner.on_change_zip_street_number()
        getaddr.assert_called_with("3811DJ", "10")

        partner._convert_to_write(partner._cache)
        self.assertFalse(partner.street_name)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)

    def test_08_res_partner_no_province(self):
        self.configure_key()
        self.load_nl_provinces()

        partner = self.create_partner()
        with self.patch_api_get_address(province=""):
            partner.on_change_zip_street_number()

        partner._convert_to_write(partner._cache)
        self.assertEqual(partner.street_name, 'Claudius Prinsenlaan')
        self.assertEqual(partner.city, 'Breda')
        self.assertFalse(partner.state_id)
        self.assertEqual(partner.street, 'Claudius Prinsenlaan 10')

    def configure_key(self):
        self.env["ir.config_parameter"].set_param(
            "l10n_nl_postcodeapi.apikey",
            "DZyipS65BT6n52jQHpVXs53r4bYK8yng3QWQT2tV",
        )

    def patch_api_get_address(
        self,
        street="Claudius Prinsenlaan",
        city="Breda",
        province="Noord-Brabant",
    ):
        getaddr = Mock()
        getaddr.return_value = SimpleNamespace(
            _data="test", street=street, city=city, province=province
        )
        return patch("pyPostcode.Api.getaddress", getaddr)

    def get_country(self, code):
        country = self.env["res.country"].search(
            [("code", "=", code)], limit=1
        )
        self.assertTrue(country)
        return country

    def create_partner(self, country="NL"):
        return self.env["res.partner"].create(
            {
                "name": "test partner",
                "street_number": "10",
                "zip": "3811DJ",
                "country_id": self.get_country(country).id,
            }
        )
