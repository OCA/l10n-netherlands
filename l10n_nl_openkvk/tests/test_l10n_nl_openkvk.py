# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
from mock import patch

from odoo.modules.module import get_resource_path
from odoo.exceptions import UserError
from odoo.tools import mute_logger
from odoo.tests.common import TransactionCase

API_KEY = 'KEYXXXXXXXXXXXNOTVALID'


class TestNLOpenKvK(TransactionCase):

    def setUp(self):
        super().setUp()
        self.set_param = self.env['ir.config_parameter'].set_param
        self.get_param = self.env['ir.config_parameter'].get_param

        self.main_partner = self.env.ref('base.main_partner')

        path_addon = 'odoo.addons.l10n_nl_kvk.'
        path_file = 'models.l10n_nl_kvk_api_handler.'
        self.api_handler = path_addon + path_file + 'KvkApiHandler.'

        self.set_param('l10n_nl_kvk_service', 'openkvk')

    @mute_logger('odoo.addons.l10n_nl_kvk.models.l10n_nl_kvk_api_handler')
    def test_01_ir_config_parameter_default(self):
        self.assertFalse(self.get_param('l10n_nl_openkvk_api_value'))
        self.set_param('l10n_nl_openkvk_api_value', API_KEY)
        self.assertTrue(self.get_param('l10n_nl_openkvk_api_value'))
        self.assertEqual(self.get_param('l10n_nl_openkvk_api_value'), API_KEY)

        self.main_partner.country_id = self.env.ref('base.nl')
        with self.assertRaises(UserError):
            wizard_action = self.main_partner.load_partner_values_from_kvk()
            self.assertFalse(wizard_action)
        with self.assertRaises(UserError):
            wizard_action = self.main_partner.load_partner_values_from_name()
            self.assertFalse(wizard_action)

        self.env['res.config.settings'].create({}).execute()
        self.assertTrue(self.get_param('l10n_nl_openkvk_api_value'))
        self.assertEqual(self.get_param('l10n_nl_openkvk_api_value'), API_KEY)

    @mute_logger('odoo.addons.l10n_nl_kvk.models.l10n_nl_kvk_api_handler')
    def test_02_ir_config_parameter_set(self):
        # Verify l10n_nl_kvk.apikey is modified
        self.set_param('l10n_nl_openkvk_api_value', API_KEY)
        api_value = self.get_param('l10n_nl_openkvk_api_value')
        self.assertEqual(api_value, API_KEY)

        main_partner = self.env.ref('base.main_partner')
        main_partner.country_id = self.env.ref('base.nl')
        with self.assertRaises(UserError):
            self.assertFalse(main_partner.load_partner_values_from_kvk())
        with self.assertRaises(UserError):
            self.assertFalse(main_partner.load_partner_values_from_name())

    def test_03_json_load(self):
        json_resource = get_resource_path(
            'l10n_nl_openkvk',
            'examples',
            'openkvk_56048785.json',
        )
        json_file = open(json_resource, 'rb').read()
        res_data = json.loads(json_file.decode())
        self.assertTrue(res_data)

        dossiernummer_list = res_data['dossiernummer']
        self.assertTrue(dossiernummer_list)
        self.assertEqual(len(dossiernummer_list), 2)

        for kvk_item in dossiernummer_list:
            self.assertEqual(kvk_item['text'], '56048785')
            self.assertEqual(kvk_item['dossiernummer'], '56048785')
            self.assertEqual(kvk_item['handelsnaam'], 'Onestein B.V.')
            self.assertTrue('id')
            self.assertTrue('link')

    def test_04_mocked_api(self):
        nl_country = self.env.ref('base.nl')

        self.main_partner.country_id = self.env.ref('base.nl')
        self.main_partner.coc_registration_number = '56048785'

        self.set_param('l10n_nl_openkvk_api_value', API_KEY)

        json_resource = get_resource_path(
            'l10n_nl_openkvk',
            'examples',
            'openkvk_56048785.json',
        )
        json_file = open(json_resource, 'rb').read()

        with patch(self.api_handler + '_retrieve_data_by_api') as _sugg_mock:
            _sugg_mock.return_value = json_file

            wizard_action = self.main_partner.load_partner_values_from_kvk()
        wizard_id = wizard_action['res_id']
        wizard = self.env['l10n.nl.kvk.preview.wizard'].browse(wizard_id)

        self.assertEqual(len(wizard.line_ids), 2)

        with patch(self.api_handler + '_retrieve_data_by_api') as _part_mock:

            rechtspersoon_resource = get_resource_path(
                'l10n_nl_openkvk',
                'examples',
                'openkvk_rechtspersoon-56048785-onestein-bv.json',
            )
            json_file = open(rechtspersoon_resource, 'rb').read()
            _part_mock.return_value = json_file

            test_line = wizard.line_ids[0]
            self.assertEqual(test_line.name, '56048785')
            self.assertEqual(test_line.kvk, '56048785')
            self.assertEqual(test_line.partner_name, 'Onestein B.V.')
            self.assertTrue(test_line.line_id_str)
            self.assertTrue(test_line.link)
            self.assertFalse(test_line.partner_city)
            self.assertEqual(test_line.entity_type, 'legal_person')

            test_line.set_partner_fields()
            self.assertEqual(self.main_partner.name, 'Onestein B.V.')
            self.assertFalse(self.main_partner.city)
            self.assertFalse(self.main_partner.zip)
            self.assertEqual(self.main_partner.vat, 'NL851956099B01')
            self.assertEqual(self.main_partner.country_id, nl_country)

            hoofdvestiging_resource = get_resource_path(
                'l10n_nl_openkvk',
                'examples',
                'openkvk_hoofdvestiging-56048785-0000-onestein-bv.json',
            )
            json_file = open(hoofdvestiging_resource, 'rb').read()
            _part_mock.return_value = json_file

            test_line = wizard.line_ids[1]
            self.assertEqual(test_line.name, '56048785')
            self.assertEqual(test_line.kvk, '56048785')
            self.assertEqual(test_line.partner_name, 'Onestein B.V.')
            self.assertTrue(test_line.line_id_str)
            self.assertTrue(test_line.link)
            self.assertEqual(test_line.partner_city, 'Breda')
            self.assertEqual(test_line.entity_type, 'headquarters')

            test_line.set_partner_fields()
            self.assertEqual(self.main_partner.name, 'Onestein B.V.')
            self.assertEqual(self.main_partner.city, 'Breda')
            self.assertEqual(self.main_partner.zip, '4814DC')
            self.assertEqual(self.main_partner.vat, 'NL851956099B01')
            self.assertEqual(self.main_partner.country_id, nl_country)

    def test_05_json_load_test_files(self):
        json_resource = get_resource_path(
            'l10n_nl_openkvk',
            'examples',
            'openkvk_hoofdvestiging-56048785-0000-onestein-bv.json',
        )
        json_file = open(json_resource, 'rb').read()
        res_data = json.loads(json_file.decode())
        self.assertTrue(res_data)

        json_resource = get_resource_path(
            'l10n_nl_openkvk',
            'examples',
            'openkvk_rechtspersoon-56048785-onestein-bv.json',
        )
        json_file = open(json_resource, 'rb').read()
        res_data = json.loads(json_file.decode())
        self.assertTrue(res_data)

    @mute_logger('odoo.addons.l10n_nl_kvk.models.l10n_nl_kvk_api_handler')
    def test_06_partner_no_action(self):
        main_partner = self.env.ref('base.main_partner')
        self.assertTrue(self.main_partner.country_id)
        self.assertFalse(main_partner.load_partner_values_from_kvk())
        self.assertFalse(main_partner.load_partner_values_from_name())

        main_partner.country_id = None
        with self.assertRaises(UserError):
            self.assertFalse(main_partner.load_partner_values_from_kvk())
        with self.assertRaises(UserError):
            self.assertFalse(main_partner.load_partner_values_from_name())

        main_partner.country_id = self.env.ref('base.nl')
        with self.assertRaises(UserError):
            self.assertFalse(main_partner.load_partner_values_from_kvk())
        with self.assertRaises(UserError):
            self.assertFalse(main_partner.load_partner_values_from_name())

        main_partner.country_id = self.env.ref('base.be')
        self.assertFalse(main_partner.load_partner_values_from_kvk())
        self.assertFalse(main_partner.load_partner_values_from_name())

    def test_07_mocked_api_multi(self):
        nl_country = self.env.ref('base.nl')

        self.main_partner.country_id = self.env.ref('base.nl')
        self.main_partner.coc_registration_number = '560487'

        self.set_param('l10n_nl_openkvk_api_value', API_KEY)

        json_resource = get_resource_path(
            'l10n_nl_openkvk',
            'examples',
            'openkvk_560487.json',
        )
        json_file = open(json_resource, 'rb').read()

        with patch(self.api_handler + '_retrieve_data_by_api') as _sugg_mock:
            _sugg_mock.return_value = json_file

            wizard_action = self.main_partner.load_partner_values_from_kvk()
        wizard_id = wizard_action['res_id']
        wizard = self.env['l10n.nl.kvk.preview.wizard'].browse(
            wizard_id
        )

        self.assertEqual(len(wizard.line_ids), 8)

        with patch(self.api_handler + '_retrieve_data_by_api') as _part_mock:
            line_id_str = 'rechtspersoon-56048785-onestein-bv'
            rechtspersoon_resource = get_resource_path(
                'l10n_nl_openkvk',
                'examples',
                'openkvk_' + line_id_str + '.json',
            )
            json_file = open(rechtspersoon_resource, 'rb').read()
            _part_mock.return_value = json_file

            test_line = wizard.line_ids[6]
            self.assertEqual(test_line.name, '56048785')
            self.assertEqual(test_line.kvk, '56048785')
            self.assertEqual(test_line.partner_name, 'Onestein B.V.')
            self.assertEqual(test_line.line_id_str, line_id_str)
            self.assertTrue(test_line.link)
            self.assertEqual(test_line.entity_type, 'legal_person')

            test_line.set_partner_fields()
            self.assertEqual(self.main_partner.name, 'Onestein B.V.')
            self.assertFalse(self.main_partner.city)
            self.assertFalse(self.main_partner.zip)
            self.assertEqual(self.main_partner.vat, 'NL851956099B01')
            self.assertEqual(self.main_partner.country_id, nl_country)

            line_id_str = 'hoofdvestiging-56048785-0000-onestein-bv'
            hoofdvestiging_resource = get_resource_path(
                'l10n_nl_openkvk',
                'examples',
                'openkvk_' + line_id_str + '.json',
            )
            json_file = open(hoofdvestiging_resource, 'rb').read()
            _part_mock.return_value = json_file

            test_line = wizard.line_ids[7]
            self.assertEqual(test_line.name, '56048785')
            self.assertEqual(test_line.kvk, '56048785')
            self.assertEqual(test_line.partner_name, 'Onestein B.V.')
            self.assertEqual(test_line.line_id_str, line_id_str)
            self.assertTrue(test_line.link)
            self.assertEqual(test_line.partner_city, 'Breda')
            self.assertEqual(test_line.entity_type, 'headquarters')

            test_line.set_partner_fields()
            self.assertEqual(self.main_partner.name, 'Onestein B.V.')
            self.assertEqual(self.main_partner.city, 'Breda')
            self.assertEqual(self.main_partner.zip, '4814DC')
            self.assertEqual(self.main_partner.vat, 'NL851956099B01')
            self.assertEqual(self.main_partner.country_id, nl_country)

    @mute_logger('odoo.addons.l10n_nl_kvk.models.l10n_nl_kvk_api_handler')
    def test_08_ir_config_parameter_set_openkvk(self):

        self.set_param('l10n_nl_kvk_service', 'openkvk')
        service_config_parameter = self.get_param('l10n_nl_kvk_service')
        self.assertTrue(service_config_parameter)
        self.assertEqual(service_config_parameter, 'openkvk')

        self.assertFalse(self.get_param('l10n_nl_kvk_api_key'))
        self.assertFalse(self.get_param('l10n_nl_kvk_api_value'))
        self.assertFalse(self.get_param('l10n_nl_openkvk_api_value'))

        self.main_partner.country_id = self.env.ref('base.nl')
        self.main_partner.coc_registration_number = '90004760'

        with self.assertRaises(UserError):
            wizard_action = self.main_partner.load_partner_values_from_kvk()
            self.assertFalse(wizard_action)

        with self.assertRaises(UserError):
            wizard_action = self.main_partner.load_partner_values_from_name()
            self.assertFalse(wizard_action)
