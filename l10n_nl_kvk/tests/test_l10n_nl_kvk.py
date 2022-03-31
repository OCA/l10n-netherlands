# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
from mock import patch

import odoo
from odoo.modules.module import get_resource_path
from odoo.exceptions import UserError
from odoo.tools import mute_logger
from odoo.tests.common import TransactionCase

API_KEY = 'KEYXXXXXXXXXXXNOTVALID'


class TestNLKvK(TransactionCase):

    def setUp(self):
        super().setUp()
        self.set_param = self.env['ir.config_parameter'].set_param
        self.get_param = self.env['ir.config_parameter'].get_param

        self.main_partner = self.env.ref('base.main_partner')

        path_addon = 'odoo.addons.l10n_nl_kvk.'
        path_file = 'models.l10n_nl_kvk_api_handler.'
        self.api_handler = path_addon + path_file + 'KvkApiHandler.'

    def test_01_ir_config_parameter_default(self):
        self.assertFalse(self.get_param('l10n_nl_kvk_service'))
        self.assertFalse(self.get_param('l10n_nl_kvk_timeout'))
        self.assertFalse(self.get_param('l10n_nl_kvk_api_key'))
        self.assertFalse(self.get_param('l10n_nl_kvk_api_value'))

        self.set_param('l10n_nl_kvk_api_key', API_KEY)
        self.set_param('l10n_nl_kvk_api_value', API_KEY)

        serv = self.env['l10n.nl.kvk.api.handler']._get_config('service')
        self.assertTrue(serv)
        self.assertEqual(serv, 'test')

        # no service specified but 'test' configuration enabled
        # so no error is raised
        self.main_partner.country_id = self.env.ref('base.nl')
        self.assertFalse(self.main_partner.is_not_nl_company)

        self.main_partner.coc_registration_number = '90004760'
        wizard_action = self.main_partner.load_partner_values_from_kvk()
        self.assertFalse(wizard_action)
        wizard_action = self.main_partner.load_partner_values_from_name()
        self.assertFalse(wizard_action)

        self.env['res.config.settings'].create({}).execute()
        self.assertTrue(self.get_param('l10n_nl_kvk_service'))
        self.assertTrue(self.get_param('l10n_nl_kvk_timeout'))
        self.assertTrue(self.get_param('l10n_nl_kvk_api_key'))
        self.assertTrue(self.get_param('l10n_nl_kvk_api_value'))

        self.assertEqual(self.get_param('l10n_nl_kvk_service'), 'test')
        self.assertEqual(int(self.get_param('l10n_nl_kvk_timeout')), 3)
        self.assertEqual(self.get_param('l10n_nl_kvk_api_key'), API_KEY)
        self.assertEqual(self.get_param('l10n_nl_kvk_api_value'), API_KEY)

    def test_02_ir_config_parameter_set_test(self):
        self.set_param('l10n_nl_kvk_service', 'test')
        service_config_parameter = self.get_param('l10n_nl_kvk_service')
        self.assertTrue(service_config_parameter)
        self.assertEqual(service_config_parameter, 'test')

        self.assertFalse(self.get_param('l10n_nl_kvk_api_key'))
        self.assertFalse(self.get_param('l10n_nl_kvk_api_value'))

        self.main_partner.country_id = self.env.ref('base.nl')
        self.assertFalse(self.main_partner.is_not_nl_company)

        self.main_partner.coc_registration_number = '90004760'

        wizard_action = self.main_partner.load_partner_values_from_kvk()
        self.assertFalse(wizard_action)

        self.main_partner.coc_registration_number = '69599084'

        wizard_action = self.main_partner.load_partner_values_from_kvk()
        self.assertTrue(wizard_action)
        wizard_action = self.main_partner.load_partner_values_from_name()
        self.assertFalse(wizard_action)

    @mute_logger('odoo.addons.l10n_nl_kvk.models.l10n_nl_kvk_api_handler')
    def test_03_ir_config_parameter_set_kvk(self):
        self.set_param('l10n_nl_kvk_service', 'kvk')
        self.assertTrue(self.get_param('l10n_nl_kvk_service'))
        self.assertEqual(self.get_param('l10n_nl_kvk_service'), 'kvk')

        # Key not set
        self.assertFalse(self.get_param('l10n_nl_kvk_api_key'))
        self.assertFalse(self.get_param('l10n_nl_kvk_api_value'))

        self.main_partner.country_id = self.env.ref('base.nl')
        self.assertFalse(self.main_partner.is_not_nl_company)

        self.main_partner.coc_registration_number = '90004760'
        with self.assertRaises(UserError):
            # Unhandled exception
            wizard_action = self.main_partner.load_partner_values_from_kvk()
            self.assertFalse(wizard_action)
        with self.assertRaises(UserError):
            # Unhandled exception
            wizard_action = self.main_partner.load_partner_values_from_name()
            self.assertFalse(wizard_action)

    def test_05_ir_config_parameter_request_timeout(self):
        timeout_config_parameter = self.get_param('l10n_nl_kvk_timeout')
        self.assertFalse(timeout_config_parameter)

        tout = self.env['l10n.nl.kvk.api.handler']._get_config('timeout')
        self.assertTrue(tout)
        self.assertEqual(tout, 3)

        timeout_config_parameter = self.get_param('l10n_nl_kvk_timeout', 3)
        self.assertTrue(timeout_config_parameter)
        self.assertEqual(timeout_config_parameter, 3)

        self.set_param('l10n_nl_kvk_timeout', 5)
        timeout_config_parameter = self.get_param('l10n_nl_kvk_timeout')
        self.assertTrue(timeout_config_parameter)
        self.assertEqual(int(timeout_config_parameter), 5)

    @mute_logger('odoo.addons.l10n_nl_kvk.models.l10n_nl_kvk_api_handler')
    def test_06_ir_config_parameter_kvk_not_set(self):
        self.set_param('l10n_nl_kvk_service', 'kvk')

        l10n_nl_kvk_api_key = self.get_param('l10n_nl_kvk_api_key')
        l10n_nl_kvk_api_value = self.get_param('l10n_nl_kvk_api_value')
        self.assertFalse(l10n_nl_kvk_api_key)
        self.assertFalse(l10n_nl_kvk_api_value)

        self.main_partner.country_id = self.env.ref('base.nl')
        with self.assertRaises(UserError):
            wizard_action = self.main_partner.load_partner_values_from_kvk()
            self.assertFalse(wizard_action)
        with self.assertRaises(UserError):
            wizard_action = self.main_partner.load_partner_values_from_name()
            self.assertFalse(wizard_action)

    def test_07_kvk_api_key_not_valid(self):
        self.set_param('l10n_nl_kvk_service', 'kvk')
        self.set_param('l10n_nl_kvk_api_key', 'apikeytest')
        self.set_param('l10n_nl_kvk_api_value', API_KEY)
        l10n_nl_kvk_api_key = self.get_param('l10n_nl_kvk_api_key')
        self.assertEqual(l10n_nl_kvk_api_key, 'apikeytest')
        l10n_nl_kvk_api_value = self.get_param('l10n_nl_kvk_api_value')
        self.assertEqual(l10n_nl_kvk_api_value, API_KEY)

        self.main_partner = self.env.ref('base.main_partner')
        self.main_partner.country_id = self.env.ref('base.nl')
        with self.assertRaises(UserError):
            wizard_action = self.main_partner.load_partner_values_from_kvk()
            self.assertFalse(wizard_action)

    def test_08_json_load(self):
        json_resource = get_resource_path(
            'l10n_nl_kvk',
            'examples',
            'kvk_69599084.json',
        )
        json_file = open(json_resource, 'rb').read()
        res_data = json.loads(json_file.decode())
        self.assertTrue(res_data)

    @odoo.tests.tagged('post_install', '-at_install')
    def test_09_mocked_api_load(self):
        my_partner = self.main_partner
        my_partner.country_id = self.env.ref('base.nl')
        self.assertFalse(self.main_partner.is_not_nl_company)

        my_partner.coc_registration_number = '69599084'

        self.set_param('l10n_nl_kvk_service', 'kvk')
        self.set_param('l10n_nl_kvk_api_key', 'apikeytest')
        self.set_param('l10n_nl_kvk_api_value', API_KEY)

        json_resource = get_resource_path(
            'l10n_nl_kvk',
            'examples',
            'kvk_69599084.json',
        )
        json_file = open(json_resource, 'rb').read()

        with patch(self.api_handler + '_retrieve_data_by_api') as _sugg_mock:
            _sugg_mock.return_value = json_file

            wizard_action = my_partner.load_partner_values_from_kvk()
        wizard_id = wizard_action['res_id']
        wizard = self.env['l10n.nl.kvk.preview.wizard'].browse(
            wizard_id
        )

        self.assertEqual(len(wizard.line_ids), 2)

        test_line = wizard.line_ids[0]
        self.assertEqual(test_line.name, '69599084')
        self.assertEqual(test_line.kvk, '69599084')
        self.assertEqual(
            test_line.partner_name,
            'Test EMZ Dagobert')
        self.assertEqual(test_line.partner_city, 'Amsterdam')
        self.assertEqual(test_line.entity_type, 'headquarters')

        test_line.set_partner_fields()
        self.assertEqual(
            my_partner.name,
            'Test EMZ Dagobert')
        self.assertEqual(my_partner.city, 'Amsterdam')
        self.assertFalse(my_partner.vat)
        self.assertEqual(my_partner.country_id, self.env.ref('base.nl'))

        test_line = wizard.line_ids[1]
        self.assertEqual(test_line.name, '69599084')
        self.assertEqual(test_line.kvk, '69599084')
        self.assertEqual(test_line.partner_name, 'Test EMZ Nevenvestiging Govert')
        self.assertEqual(test_line.partner_city, 'Maastricht')
        self.assertEqual(test_line.entity_type, 'branch')

        test_line.set_partner_fields()
        self.assertEqual(my_partner.name, 'Test EMZ Nevenvestiging Govert')
        self.assertEqual(my_partner.city, 'Maastricht')
        self.assertFalse(my_partner.vat)
        self.assertEqual(my_partner.country_id, self.env.ref('base.nl'))

    def test_10_api_load_test_mode(self):

        my_partner = self.main_partner
        my_partner.country_id = self.env.ref('base.nl')
        my_partner.coc_registration_number = '69599084'
        nl_country = self.env.ref('base.nl')

        self.set_param('l10n_nl_kvk_service', 'test')
        self.set_param('l10n_nl_kvk_api_key', 'apikeytest')
        self.set_param('l10n_nl_kvk_api_value', API_KEY)

        wizard_action = my_partner.load_partner_values_from_kvk()
        self.assertTrue(wizard_action)
        wizard_id = wizard_action['res_id']
        wizard = self.env['l10n.nl.kvk.preview.wizard'].browse(
            wizard_id
        )

        self.assertEqual(len(wizard.line_ids), 2)

        test_line = wizard.line_ids[1]
        self.assertEqual(test_line.name, '69599084')
        self.assertEqual(test_line.kvk, '69599084')
        self.assertEqual(
            test_line.partner_name,
            'Test EMZ Nevenvestiging Govert')
        self.assertEqual(test_line.partner_city, 'Maastricht')
        self.assertEqual(test_line.entity_type, 'branch')

        test_line.set_partner_fields()
        self.assertEqual(my_partner.name,
                         'Test EMZ Nevenvestiging Govert')
        self.assertEqual(my_partner.city, 'Maastricht')
        self.assertFalse(my_partner.vat)
        self.assertEqual(my_partner.country_id, nl_country)

        test_line = wizard.line_ids[0]
        self.assertEqual(test_line.name, '69599084')
        self.assertEqual(test_line.kvk, '69599084')
        self.assertEqual(test_line.partner_name, 'Test EMZ Dagobert')
        self.assertEqual(test_line.partner_city, 'Amsterdam')
        self.assertEqual(test_line.entity_type, 'headquarters')

        test_line.set_partner_fields()
        self.assertEqual(my_partner.name, 'Test EMZ Dagobert')
        self.assertEqual(my_partner.city, 'Amsterdam')
        self.assertFalse(my_partner.vat)
        self.assertEqual(my_partner.country_id, nl_country)

    @mute_logger('odoo.addons.l10n_nl_kvk.models.l10n_nl_kvk_api_handler')
    def test_11_api_internal_server_error(self):

        my_partner = self.main_partner
        my_partner.country_id = self.env.ref('base.nl')
        my_partner.coc_registration_number = 'test'

        self.set_param('l10n_nl_kvk_service', 'kvk')
        self.set_param('l10n_nl_kvk_api_key', 'apikeytest')
        self.set_param('l10n_nl_kvk_api_value', API_KEY)

        with patch(self.api_handler + '_get_url_query_kvk_api') as _my_mock:
            _my_mock.return_value = \
                'https://api.kvk.nl/test/api/v1/'

            with self.assertRaises(UserError):
                wizard_action = my_partner.load_partner_values_from_kvk()
                self.assertFalse(wizard_action)

            with self.assertRaises(UserError):
                wizard_action = my_partner.load_partner_values_from_name()
                self.assertFalse(wizard_action)

    @mute_logger('odoo.addons.l10n_nl_kvk.models.l10n_nl_kvk_api_handler')
    def test_12_api_no_result(self):

        self.main_partner.country_id = self.env.ref('base.nl')
        self.assertFalse(self.main_partner.is_not_nl_company)

        self.main_partner.coc_registration_number = 'not existing'

        self.set_param('l10n_nl_kvk_service', 'kvk')
        self.set_param('l10n_nl_kvk_api_key', 'apikeytest')
        self.set_param('l10n_nl_kvk_api_value', API_KEY)

        with self.assertRaises(UserError):
            wizard_action = self.main_partner.load_partner_values_from_kvk()
            self.assertFalse(wizard_action)

        with self.assertRaises(UserError):
            wizard_action = self.main_partner.load_partner_values_from_name()
            self.assertFalse(wizard_action)

    def test_13_api_load_with_wizard(self):

        my_partner = self.env.ref('base.main_partner')
        my_partner.country_id = self.env.ref('base.nl')
        my_partner.coc_registration_number = '68727720'
        nl_country = self.env.ref('base.nl')

        self.set_param('l10n_nl_kvk_service', 'test')
        self.set_param('l10n_nl_kvk_api_key', 'apikeytest')
        self.set_param('l10n_nl_kvk_api_value', API_KEY)

        wizard_action = my_partner.load_partner_values_from_kvk()
        self.assertTrue(wizard_action)
        wizard_id = wizard_action['res_id']
        wizard = self.env['l10n.nl.kvk.preview.wizard'].browse(
            wizard_id
        )

        self.assertEqual(len(wizard.line_ids), 2)

        test_line = wizard.line_ids[1]
        self.assertEqual(test_line.name, '68727720')
        self.assertEqual(test_line.kvk, '68727720')
        self.assertEqual(test_line.partner_name, 'Test NV Katrien')
        self.assertFalse(test_line.partner_city)
        self.assertEqual(test_line.entity_type, 'legal_person')

        test_line.set_partner_fields()
        self.assertEqual(my_partner.name, 'Test NV Katrien')
        self.assertFalse(my_partner.city)
        self.assertFalse(my_partner.vat)
        self.assertEqual(my_partner.country_id, nl_country)

        test_line = wizard.line_ids[0]
        self.assertEqual(test_line.name, '68727720')
        self.assertEqual(test_line.kvk, '68727720')
        self.assertEqual(test_line.partner_name, 'Test NV Katrien')
        self.assertEqual(test_line.partner_city, 'Veendam')
        self.assertEqual(test_line.entity_type, 'headquarters')

        test_line.set_partner_fields()
        self.assertEqual(my_partner.name, 'Test NV Katrien')
        self.assertEqual(my_partner.city, 'Veendam')
        self.assertFalse(my_partner.vat)
        self.assertEqual(my_partner.country_id, nl_country)

    def test_14_api_load_no_wizard(self):

        my_partner = self.env.ref('base.main_partner')
        my_partner.country_id = self.env.ref('base.nl')
        my_partner.coc_registration_number = '90004760'
        nl_country = self.env.ref('base.nl')

        self.set_param('l10n_nl_kvk_service', 'test')
        self.set_param('l10n_nl_kvk_api_key', 'apikeytest')
        self.set_param('l10n_nl_kvk_api_value', API_KEY)

        wizard_action = my_partner.load_partner_values_from_kvk()
        self.assertFalse(wizard_action)

        wizard_action = my_partner.load_partner_values_from_name()
        self.assertFalse(wizard_action)

        # partner fields directly set (without popup)
        self.assertEqual(my_partner.name, 'Local Funzoom N.V.')
        self.assertEqual(my_partner.city, 'Leiderdorp')
        self.assertFalse(my_partner.vat)
        self.assertEqual(my_partner.country_id, nl_country)

    @mute_logger('odoo.addons.l10n_nl_kvk.models.l10n_nl_kvk_api_handler')
    def test_15_api_no_nl(self):

        self.main_partner.country_id = self.env.ref('base.be')
        self.assertTrue(self.main_partner.is_not_nl_company)

        self.main_partner.coc_registration_number = 'not existing'

        self.set_param('l10n_nl_kvk_service', 'kvk')
        self.set_param('l10n_nl_kvk_api_key', 'apikeytest')
        self.set_param('l10n_nl_kvk_api_value', API_KEY)

        wizard_action = self.main_partner.load_partner_values_from_kvk()
        self.assertFalse(wizard_action)

        wizard_action = self.main_partner.load_partner_values_from_name()
        self.assertFalse(wizard_action)

    def test_16_api_load_no_results(self):

        my_partner = self.env.ref('base.main_partner')
        my_partner_name = my_partner.name
        my_partner_city = my_partner.city
        my_partner_vat = my_partner.vat
        my_partner.country_id = self.env.ref('base.nl')
        my_partner.coc_registration_number = '90004841'

        self.set_param('l10n_nl_kvk_service', 'test')
        self.set_param('l10n_nl_kvk_api_key', 'apikeytest')
        self.set_param('l10n_nl_kvk_api_value', API_KEY)

        with self.assertRaises(UserError):
            wizard_action = my_partner.load_partner_values_from_kvk()
            self.assertFalse(wizard_action)

        with self.assertRaises(UserError):
            wizard_action = my_partner.load_partner_values_from_name()
            self.assertFalse(wizard_action)

        # partner not changed
        self.assertEqual(my_partner.name, my_partner_name)
        self.assertEqual(my_partner.city, my_partner_city)
        self.assertEqual(my_partner.vat, my_partner_vat)
        self.assertEqual(my_partner.country_id, self.env.ref('base.nl'))
