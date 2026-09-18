# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# API documentation: https://docs.liza.nl

import os
from unittest.mock import patch

from freezegun import freeze_time

from odoo import exceptions
from odoo.tests import Form, new_test_user, users
from odoo.tools import mute_logger

from ..liza_const import DATA_KEYS, FILL_FIELD_MAP
from ..models.res_partner import (
    LIZA_SYNC_STATUS_ACTIVE,
    LIZA_SYNC_STATUS_NONE,
    LIZA_SYNC_STATUS_PENDING,
)
from .common import TEST_LOGIN, TEST_PASSWORD, LizaTestCommon

# Values saved in cassette. We don't test
# - dates (FakeDates)
# - related record IDs (which might differ to demo DB)
# - URL with varying tokens
EXPECTED_VALUES = {
    "liza_addedValue": -20251636.08,
    "liza_addedValue_unset": False,
    "liza_address_enable": True,
    "liza_average_fte": 128.7,
    "liza_average_fte_unset": False,
    "liza_balance_data_enable": True,
    "liza_balance_year": "2024",
    "liza_city": "Sint-Niklaas",
    "liza_companystatus": "Actif",
    "liza_companystatus_code": "0",
    "liza_companystatus_enable": True,
    "liza_creditLimit": 0,
    "liza_creditLimit_enable": True,
    "liza_creditLimit_info": "Résultat très négatif",
    "liza_creditLimit_unset": False,
    "liza_email": "info@svk.be",
    "liza_email_enable": True,
    "liza_endDate": False,
    "liza_endDate_enable": True,
    "liza_equityCapital": 7533441.94,
    "liza_equityCapital_unset": False,
    "liza_image": "neg-34.png",
    "liza_jur_form": "SA",
    "liza_jur_form_enable": True,
    "liza_main_industry_enable": True,
    "liza_name": "Scheerders van Kerchove's Verenigde Fabrieken",
    "liza_name_enable": True,
    "liza_phone": "037604900",
    "liza_phone_enable": True,
    "liza_prefLang_enable": True,
    "liza_registry": "0405056855",
    "liza_registry_enable": True,
    "liza_result": 8485555.32,
    "liza_result_unset": False,
    "liza_score": "-3.4",
    "liza_score_enable": True,
    "liza_startDate_enable": True,
    "liza_street": "Aerschotstraat 114",
    "liza_turnover": 27246603.74,
    "liza_turnover_unset": False,
    "liza_url": "https://www.liza.nl/fr/c/0405056855/svk",
    "liza_url_enable": True,
    "liza_url_report_enable": True,
    "liza_vat": "BE 0405.056.855",
    "liza_vat_enable": True,
    "liza_vat_liable": True,
    "liza_vat_liable_enable": True,
    "liza_warnings_enable": True,
    "liza_website": "https://svk.be",
    "liza_website_enable": True,
    "liza_zip": "9100",
    "liza_commercial_name": False,
    "liza_commercial_name_enable": True,
    "liza_country_code": "BE",
    "liza_industries": "23650 - Fabrication d’ouvrages en fibre-ciment\n"
    "23650 - Fabrication d’ouvrages en fibre-ciment\n"
    "18120 - Autres activités d’imprimerie\n"
    "23321 - Fabrication de briques",
    "liza_industries_enable": True,
    "liza_liable_party": False,
    "liza_liable_party_enable": False,
    "liza_main_industry": "23650 - Fabrication d’ouvrages en fibre-ciment",
    "liza_peppol": True,
}


class TestApiLiza(LizaTestCommon):
    LIZA_ALLOWED_HOSTNAMES = ("connect.liza.nl",)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        french = cls.env.ref("base.lang_fr")
        french.install_lang()
        french.active = True
        cls.belgium = cls.env.ref("base.be")
        cls.france = cls.env.ref("base.fr")
        cls.normal_user = new_test_user(
            cls.env, "normal_user", "base.group_partner_manager"
        )
        cls.cwb_user = new_test_user(cls.env, "cwb_user", "liza_base.liza_download")
        # Results are language-dependent
        cls.cwb_user.lang = "FR"

    def _enable_followup(self):
        self.company.write({"liza_followup_enable": True})
        self.assertTrue(self.company.liza_followup_enable)

    def _create_partner(self, values=None):
        if values is None:
            # Partner data in cassette and EXPECTED_VALUES
            values = {
                "name": "Test",
                "vat": "BE0405056855",
            }
        values.update({"is_company": True})
        return self.env["res.partner"].create(values)

    def test_ensure_credentials(self):
        self._set_credentials()
        self.assertTrue(self.env["res.partner"]._liza_ensure_credentials())

    @users("normal_user")
    def test_liza_access(self):
        self._set_credentials()
        partner = self._create_partner()
        with self.assertRaisesRegex(
            exceptions.AccessDenied,
            "Liza: You don't have access to download data",
        ):
            partner.liza_button_enhance()

    @users("cwb_user")
    def test_api2(self):
        self._set_credentials()
        self.env["ir.config_parameter"].sudo().set_param(
            "liza.alacarte",
            "https://connect.liza.nl/V1.3/alacarteservice.asmx",
        )
        partner = self._create_partner()
        with self.assertRaisesRegex(
            exceptions.ValidationError,
            "Liza: Please use the address for API V2.0",
        ):
            partner.liza_button_enhance()

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_credentials_wizard(self):
        login = os.environ.get("LIZA_TEST_LOGIN", TEST_LOGIN)
        password = os.environ.get("LIZA_TEST_PASSWORD", TEST_PASSWORD)
        partner = self._create_partner(
            {
                "name": "Acsone SA",
            }
        )
        action = partner.liza_button_enhance()
        # Credentials wizard got returned
        self.assertEqual(action.get("res_model"), "liza_base.credential_wizard_base")

        credentials_wizard = Form.from_action(self.env, action)
        credentials_wizard.liza_login = login
        credentials_wizard.liza_password = password
        credentials_wizard.save()
        credentials_wizard.record.with_context(
            active_id=partner.id
        ).save_liza_login_pwd()
        self.assertEqual(self.company.liza_login, login)
        self.assertEqual(self.company.liza_password, password)

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_liza_button_vat(self):
        self._set_credentials()
        partner = self._create_partner()
        self.assertTrue(partner.liza_show_button_enhance)
        result = partner.liza_button_enhance()
        self.assertEqual(result.get("params", {}).get("type"), "success")
        self.assertTrue(partner.liza_show_button_address)
        self.assertTrue(partner.liza_show_tab)
        for liza_field, expected_result in EXPECTED_VALUES.items():
            self.assertEqual(partner[liza_field], expected_result)

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_liza_button_registry(self):
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Test",
                "company_registry": "0405056855",
                "country_id": self.belgium.id,
            }
        )
        self.assertTrue(partner.liza_show_button_enhance)
        partner.liza_button_enhance()
        for liza_field, expected_result in EXPECTED_VALUES.items():
            self.assertEqual(partner[liza_field], expected_result)

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_liza_button_search(self):
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Scheerders van Kerchoves Verenigde Fabrieken",
                "country_id": self.belgium.id,
            }
        )
        self.assertTrue(partner.liza_show_button_enhance)
        action = partner.liza_button_enhance()

        # Search wizard got returned
        self.assertEqual(action.get("res_model"), "liza.search.wizard")
        wizard = self.env["liza.search.wizard"].browse(action.get("res_id"))
        self.assertTrue(len(wizard.line_ids) > 0)
        first_result = wizard.line_ids[0]
        first_result.select()
        for liza_field, expected_result in EXPECTED_VALUES.items():
            self.assertEqual(partner[liza_field], expected_result)

    @users("cwb_user")
    def test_search_wizard_registry_applies_single_company(self):
        """Entering a Company ID in the search wizard resolves to a single
        company and stores the registration number on the contact."""
        self._set_credentials()
        partner = self._create_partner(
            {"name": "AG Immo", "country_id": self.belgium.id}
        )
        # Liza returns one company for an exact Company ID lookup (a dict, not
        # a SearchCompanies list).
        record = self._followup_record(
            ref=False, registry="0405056855", country="BE", in_followup=False
        )
        record["CompanyName"] = {"IsEnabled": True, "Value": "AG Immo NV"}
        wizard = self.env["liza.search.wizard"].create(
            {
                "partner_id": partner.id,
                "company_registry": "0405056855",
                "country_code": "BE",
            }
        )
        with patch.object(type(partner), "_liza_call_get", return_value=("", record)):
            result = wizard.liza_search()
        # The wizard applied the company directly instead of listing lines.
        self.assertEqual(result.get("tag"), "display_notification")
        self.assertEqual(partner.liza_registry, "0405056855")
        self.assertEqual(partner.company_registry, "0405056855")

    @users("cwb_user")
    def test_copy_address_keeps_registry_when_liza_has_none(self):
        """Filling data must not wipe a registration number the user entered
        when Liza has no registration number for the company."""
        partner = self._create_partner(
            {
                "name": "AG Immo",
                "company_registry": "0405056855",
                "country_id": self.belgium.id,
            }
        )
        # Simulate an enrichment that returned a name but no registration number.
        partner.write({"liza_name": "AG Immo", "liza_registry": False})
        partner.liza_button_copy_address()
        self.assertEqual(partner.company_registry, "0405056855")

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_liza_button_search_missing_values(self):
        """
        Test missing country and missing country code in VAT
        """
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Test",
                "vat": "0405056855",
            }
        )
        with self.assertRaisesRegex(
            exceptions.ValidationError, "Missing values for company search"
        ):
            partner.liza_button_enhance()

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_liza_button_wrong_vat(self):
        """
        Test invalid VAT (liza error)
        """
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Test",
                "vat": "123123123",
                "country_id": self.belgium.id,
            }
        )
        with self.assertRaisesRegex(exceptions.ValidationError, "Liza status"):
            partner.liza_button_enhance()

    @users("cwb_user")
    def test_liza_button_wrong_country(self):
        """
        Test invalid country
        """
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Test",
                "company_registry": "0405056855",
                "country_id": self.env.ref("base.uk").id,
            }
        )
        with self.assertRaisesRegex(
            exceptions.ValidationError, "Liza only supports companies based in"
        ):
            partner.liza_button_enhance()

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_liza_copy_data(self):
        self._set_credentials()
        disabled_fields = [
            "fill_liza_street",
            "fill_liza_zip",
            "fill_liza_city",
            "fill_liza_country_id",
        ]
        self.company.sudo().write(
            {disabled_field: False for disabled_field in disabled_fields}
        )
        partner = self._create_partner()
        partner.liza_button_enhance()
        result = partner.liza_button_copy_address()
        self.assertEqual(result.get("params", {}).get("type"), "success")

        for liza_field, odoo_field in FILL_FIELD_MAP.items():
            # Disabled fields are not copied
            if f"fill_{liza_field}" in disabled_fields:
                self.assertNotEqual(partner[liza_field], partner[odoo_field])
            else:
                self.assertEqual(partner[liza_field], partner[odoo_field])
        self.company.sudo().write(
            {disabled_field: True for disabled_field in disabled_fields}
        )
        partner.liza_button_copy_address()
        for liza_field, odoo_field in FILL_FIELD_MAP.items():
            # All fields are copied
            self.assertEqual(partner[liza_field], partner[odoo_field])

    @users("normal_user")
    @freeze_time("2026-01-29")
    def test_access_copy_data(self):
        partner = self._create_partner()
        partner.with_user(self.cwb_user).liza_button_enhance()
        with self.assertRaisesRegex(
            exceptions.AccessDenied, "Liza: You don't have access"
        ):
            partner.liza_button_copy_address()

    @users("cwb_user")
    @freeze_time("2026-02-10")
    def test_liza_push(self):
        self._set_credentials()
        self._enable_followup()
        partner = self._create_partner()
        self.assertTrue(partner.liza_followup_enable)
        partner.liza_button_enhance()
        result = partner.action_push_followup_partners()
        msg = result.get("params").get("message")
        self.assertEqual(partner.liza_sync_status, LIZA_SYNC_STATUS_PENDING)
        self.assertIn("Added 1 contact(s)", msg)

    @freeze_time("2026-03-06")
    def test_liza_cron(self):
        self._set_credentials()
        self._enable_followup()
        # Use specific details pushed manually and saved in cassette.
        # We don't push in this test
        partner = self._create_partner(
            {
                "name": "Test",
                "company_registry": "0878194448",
                "country_id": self.belgium.id,
                "liza_sync_reference": "38b9ef0a-8c8a-4c53-852e-d413470be836",
            }
        )
        self.assertEqual(partner.liza_sync_status, LIZA_SYNC_STATUS_NONE)
        self.env["res.partner"]._cron_liza_followup()
        self.assertEqual(partner.liza_sync_status, LIZA_SYNC_STATUS_ACTIVE)
        # Ensure new partner data has been filled to contact
        self.assertEqual(partner.name, partner.liza_name)

    def _followup_record(self, ref, registry, country, in_followup):
        """Build a minimal (all-disabled) Alerts_FetchBulk record with only the
        fields we need enabled, parseable by _liza_parse."""
        record = {
            api_key: {"IsEnabled": False, "Value": None}
            for api_key in DATA_KEYS.values()
        }
        record["CountryCode"] = {"IsEnabled": True, "Value": country}
        record["RegistrationNumber"] = {"IsEnabled": True, "Value": registry}
        record["IsInFollowUp"] = {"IsEnabled": True, "Value": in_followup}
        record["FollowUpReference"] = {"IsEnabled": True, "Value": ref}
        return record

    def test_find_followup_partner_falls_back_to_registry(self):
        # A record without a follow-up reference is matched on registry + country
        partner = self._create_partner(
            {"name": "AG Immo", "country_id": self.belgium.id}
        )
        partner.write({"liza_registry": "0747793685", "liza_country_code": "BE"})
        found = self.env["res.partner"]._liza_find_followup_partner(
            False, {"liza_registry": "0747793685", "liza_country_code": "BE"}
        )
        self.assertEqual(found, partner)

    @mute_logger("odoo.addons.liza_base.models.res_partner")
    @patch("odoo.addons.liza_base.models.res_partner.liza_sync")
    def test_cron_removal_from_alerts_resets_status(self, mock_sync):
        self._set_credentials()
        ref = "84926859-5733-4618-8d0c-2ef137374906"
        partner = self._create_partner(
            {
                "name": "AG Immo",
                "company_registry": "0747793685",
                "country_id": self.belgium.id,
                "liza_sync_reference": ref,
            }
        )
        partner.write(
            {
                "liza_sync": True,
                "liza_sync_status": LIZA_SYNC_STATUS_ACTIVE,
                "liza_registry": "0747793685",
                "liza_country_code": "BE",
            }
        )
        record = self._followup_record(ref, "0747793685", "BE", in_followup=False)
        # First call returns the record; once we confirm it, Liza returns an
        # empty batch, so the follow-up loop terminates.
        empty_batch = (
            0,
            {
                "CompanyResponses": {"CompanyResponseV2_0": []},
                "RemainingChanges": {"RemainingChangesCount": 0},
            },
        )
        mock_sync.side_effect = [
            (
                0,
                {
                    "CompanyResponses": {"CompanyResponseV2_0": [record]},
                    "RemainingChanges": {"RemainingChangesCount": 0},
                },
            ),
            empty_batch,
        ]
        self.env["res.partner"]._cron_liza_followup()
        # Removed from Alerts -> status back to none, no longer synced
        self.assertEqual(partner.liza_sync_status, LIZA_SYNC_STATUS_NONE)
        self.assertFalse(partner.liza_sync)
        # The contact itself must not be blanked by the removal
        self.assertEqual(partner.name, "AG Immo")

    @mute_logger("odoo.addons.liza_base.models.res_partner")
    @patch("odoo.addons.liza_base.models.res_partner.liza_sync")
    def test_cron_followup_skips_unparseable_record(self, mock_sync):
        """A single badly structured record must not abort the whole batch."""
        self._set_credentials()
        # Missing the expected data keys, so _liza_parse raises while parsing.
        bad_record = {"FollowUpReference": {"Value": "ref-bad"}}
        mock_sync.return_value = (
            0,
            {
                "CompanyResponses": {"CompanyResponseV2_0": [bad_record]},
                "RemainingChanges": {"RemainingChangesCount": 0},
            },
        )
        # Must complete without raising despite the unparseable record.
        self.env["res.partner"]._cron_liza_followup()
        log = self.env["ir.logging"].search(
            [("func", "=", "_cron_liza_followup"), ("level", "=", "WARNING")],
            limit=1,
        )
        self.assertTrue(log)
        self.assertIn("ref-bad", log.message)

    @users("cwb_user")
    @freeze_time("2026-03-10")
    def test_liza_push_multi(self):
        self._set_credentials()
        self._enable_followup()
        valid_partner = self._create_partner()
        # Use specific ref saved in cassette.
        invalid_partner = self._create_partner(
            {
                "name": "Test",
                "company_registry": "123123123",
                "country_id": self.belgium.id,
                "liza_sync_reference": "38b9ef0a-8c8a-4c53-852e-d413470be836",
            }
        )
        result = (valid_partner | invalid_partner).action_push_followup_partners()
        msg = result.get("params").get("message")
        self.assertIn("Added 1 contact(s)", msg)
        self.assertIn("Failed to push 1 contact(s)", msg)
        self.assertIn("n’est pas un numero de registration", invalid_partner.liza_error)

    def test_push_uses_vat_country_not_address_country(self):
        """
        A Belgian partner (BE VAT) with a Dutch address must send CountryCode=BE
        to the alerts API, not NL from the address.
        """
        self._set_credentials()
        self._enable_followup()
        partner = self._create_partner(
            {
                "name": "Test",
                "vat": "BE0405056855",
                "country_id": self.env.ref("base.nl").id,
            }
        )
        pushed_lists = []

        def mock_push(self_inner, partner_list):
            pushed_lists.append(partner_list)
            return "", [], 1

        with patch.object(type(partner), "_push_followup_partners", mock_push):
            partner.action_push_followup_partners()

        self.assertEqual(len(pushed_lists), 1)
        self.assertEqual(len(pushed_lists[0]), 1)
        self.assertEqual(pushed_lists[0][0]["CountryCode"], "BE")

    def test_enhance_uses_vat_country_not_address_country(self):
        """
        A partner with a Belgian VAT but an address in a non-allowed country (UK)
        must not be rejected during enhance — the country is determined from the VAT,
        not the address.
        """
        partner = self._create_partner(
            {
                "name": "Test",
                "vat": "BE0405056855",
                "country_id": self.env.ref("base.uk").id,
            }
        )
        called_args = []

        def mock_call_get(self_inner, args):
            called_args.append(dict(args))
            return "mocked", None

        with patch.object(type(partner), "_liza_call_get", mock_call_get):
            errors = partner._liza_enhance()

        self.assertTrue(called_args, "API call should have been attempted")
        self.assertEqual(called_args[0].get("country_code"), "BE")
        self.assertFalse(
            any("only supports companies" in (e or "") for e in errors),
            "Partner must not be rejected due to address country",
        )

    def test_nl_fields(self):
        self._set_credentials()
        nl_partner = self._create_partner(
            {
                "name": "Test",
                "vat": "NL 810433941 B01",
            }
        )
        nl_partner.liza_button_enhance()
        self.assertTrue(nl_partner.liza_rsin_number_enable)
        self.assertTrue(nl_partner.liza_liable_party_enable)
        self.assertEqual(
            nl_partner.liza_liable_party,
            "Coolblue Holding (NL)\nVAT: NL 810437466 B01\nEst. 01/01/2014",
        )
        self.assertEqual(nl_partner.liza_rsin_number, "810433941")

    @users("cwb_user")
    @freeze_time("2026-07-02")
    def test_liza_button_vat_fr(self):
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Test FR",
                "vat": "FR51306138900",
            }
        )
        self.assertTrue(partner.liza_show_button_enhance)
        result = partner.liza_button_enhance()
        self.assertEqual(result.get("params", {}).get("type"), "success")
        self.assertTrue(partner.liza_show_tab)
        self.assertEqual(partner.liza_country_code, "FR")

    @users("cwb_user")
    @freeze_time("2026-07-02")
    def test_liza_button_registry_fr(self):
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Test FR",
                "company_registry": "652014051",
                "country_id": self.france.id,
            }
        )
        self.assertTrue(partner.liza_show_button_enhance)
        partner.liza_button_enhance()
        self.assertEqual(partner.liza_country_code, "FR")

    @users("cwb_user")
    def test_search_wizard_reopens_search_button_on_new_terms(self):
        """After a result list is shown the search button is hidden; changing a
        search term must bring it back so the user can search again."""
        partner = self._create_partner({"name": "Test", "country_id": self.belgium.id})
        wizard = self.env["liza.search.wizard"].create({"partner_id": partner.id})
        wizard.display_search_button = False
        wizard.search_term = "Another name"
        wizard._onchange_search_terms()
        self.assertTrue(wizard.display_search_button)

    @users("cwb_user")
    def test_search_wizard_without_credentials_asks_for_them(self):
        """Searching without credentials must open the credentials wizard
        instead of calling Liza."""
        self.company.write({"liza_login": False, "liza_password": False})
        partner = self._create_partner({"name": "Test", "country_id": self.belgium.id})
        wizard = self.env["liza.search.wizard"].create({"partner_id": partner.id})
        action = wizard.liza_search()
        self.assertEqual(action.get("res_model"), "liza_base.credential_wizard_base")

    @users("cwb_user")
    def test_search_wizard_reports_api_error(self):
        """An error from Liza is shown to the user, not swallowed."""
        self._set_credentials()
        partner = self._create_partner({"name": "Test", "country_id": self.belgium.id})
        wizard = self.env["liza.search.wizard"].create(
            {"partner_id": partner.id, "vat": "BE0405056855", "country_code": "BE"}
        )
        with patch.object(
            type(partner), "_liza_call_get", return_value=("Liza error 303", [])
        ):
            with self.assertRaisesRegex(exceptions.ValidationError, "Liza error 303"):
                wizard.liza_search()

    @users("cwb_user")
    def test_search_wizard_reports_unknown_identifier(self):
        """An exact VAT/Company ID lookup that Liza does not know returns an
        empty response: the user must be told, not left with a silent no-op."""
        self._set_credentials()
        partner = self._create_partner({"name": "Test", "country_id": self.belgium.id})
        wizard = self.env["liza.search.wizard"].create(
            {"partner_id": partner.id, "vat": "BE0999999999", "country_code": "BE"}
        )
        with patch.object(type(partner), "_liza_call_get", return_value=("", {})):
            with self.assertRaisesRegex(exceptions.ValidationError, "no company found"):
                wizard.liza_search()

    @users("cwb_user")
    def test_search_wizard_vat_applies_single_company(self):
        """The VAT counterpart of the Company ID lookup: the number the user
        typed is stored on the contact together with the country."""
        self._set_credentials()
        partner = self._create_partner({"name": "AG Immo"})
        record = self._followup_record(
            ref=False, registry="0405056855", country="BE", in_followup=False
        )
        record["CompanyName"] = {"IsEnabled": True, "Value": "AG Immo NV"}
        wizard = self.env["liza.search.wizard"].create(
            {
                "partner_id": partner.id,
                "vat": "BE0405056855",
                "country_code": "BE",
            }
        )
        with patch.object(type(partner), "_liza_call_get", return_value=("", record)):
            result = wizard.liza_search()
        self.assertEqual(result.get("tag"), "display_notification")
        self.assertEqual(partner.vat, "BE0405056855")
        # The response was applied without a second call to Liza.
        self.assertEqual(partner.liza_registry, "0405056855")
        self.assertFalse(partner.liza_error)

    @users("cwb_user")
    def test_search_wizard_single_company_without_country(self):
        """A wizard without a country still applies the company: the country
        lookup is simply skipped."""
        self._set_credentials()
        partner = self._create_partner(
            {"name": "AG Immo", "country_id": self.belgium.id}
        )
        record = self._followup_record(
            ref=False, registry="0405056855", country="BE", in_followup=False
        )
        record["CompanyName"] = {"IsEnabled": True, "Value": "AG Immo NV"}
        wizard = self.env["liza.search.wizard"].create(
            {"partner_id": partner.id, "vat": "BE0405056855", "country_code": False}
        )
        with patch.object(type(partner), "_liza_call_get", return_value=("", record)):
            result = wizard.liza_search()
        self.assertEqual(result.get("tag"), "display_notification")
        self.assertEqual(partner.vat, "BE0405056855")

    @users("cwb_user")
    def test_push_requires_credentials(self):
        self.company.write({"liza_login": False, "liza_password": False})
        partner = self._create_partner()
        with self.assertRaisesRegex(
            exceptions.ValidationError, "Missing Liza credentials"
        ):
            partner.action_push_followup_partners()

    @users("cwb_user")
    def test_push_flags_partners_that_cannot_be_identified(self):
        """Partners Liza cannot look up are flagged with a reason on the record
        instead of being pushed and silently rejected."""
        self._set_credentials()
        self._enable_followup()
        no_identifier = self._create_partner(
            {"name": "No identifier", "country_id": self.belgium.id}
        )
        no_country = self._create_partner({"name": "No country"})
        no_country.write({"company_registry": "0405056855", "country_id": False})
        bad_country = self._create_partner(
            {"name": "Unsupported country", "country_id": self.env.ref("base.de").id}
        )
        bad_country.write({"company_registry": "HRB12345"})
        partners = no_identifier + no_country + bad_country
        # Nothing is eligible, so no call should reach Liza.
        with patch.object(
            type(partners), "_push_followup_partners", return_value=("", [], 0)
        ) as mock_push:
            partners.action_push_followup_partners()
        self.assertEqual(mock_push.call_args.args[0], [])
        self.assertIn("Missing VAT or Company Registry", no_identifier.liza_error)
        self.assertIn("Missing country", no_country.liza_error)
        self.assertIn("Invalid country", bad_country.liza_error)
        # None of them may be marked as being tracked by Liza.
        for partner in partners:
            self.assertEqual(partner.liza_sync_status, LIZA_SYNC_STATUS_NONE)
