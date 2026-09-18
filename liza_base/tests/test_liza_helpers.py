# Copyright 2026 Dynapps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# Unit tests for the pure Liza helper functions (no API call / cassette needed).

from unittest.mock import MagicMock, patch

from freezegun import freeze_time
from lxml import etree
from requests.exceptions import ConnectionError as RequestsConnectionError
from zeep.exceptions import Fault, TransportError

from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon

from ..liza_const import BALANCE_FIELDS, BALANCE_NESTED_FIELDS
from ..liza_format import (
    format_date,
    format_float_value,
    format_industry,
    format_warnings,
)
from ..liza_utils import (
    _format_liza_fault,
    _liza_create_hash,
    _liza_get,
    _liza_get_service_args,
    get_balance_values,
    get_country_code_from_vat,
    get_enable_field,
    get_liza_country_code,
    liza_client,
)


class TestLizaHelpers(BaseCommon):
    @freeze_time("2026-07-24")
    def test_create_hash_matches_documented_example(self):
        """Reproduce the reference hash from the Liza API guidelines.

        docs.liza.nl: today=20260724, login=MYNAME, password=ABC123,
        secret=BD5899FE-2759-4944-8948-B5D4063C05CB
        -> 6984600a575f1435c2e6bde5adf63ffa12f1a804
        """
        self.assertEqual(
            _liza_create_hash(
                "MYNAME", "ABC123", "BD5899FE-2759-4944-8948-B5D4063C05CB"
            ),
            "6984600a575f1435c2e6bde5adf63ffa12f1a804",
        )

    def test_get_liza_country_code_maps_french_territories(self):
        # French overseas territories resolve to FR
        self.assertEqual(get_liza_country_code("GP"), "FR")  # Guadeloupe
        self.assertEqual(get_liza_country_code("mq"), "FR")  # case-insensitive
        # Supported and unsupported mainland codes pass through unchanged
        self.assertEqual(get_liza_country_code("NL"), "NL")
        self.assertEqual(get_liza_country_code("DE"), "DE")
        # Empty stays empty
        self.assertFalse(get_liza_country_code(""))
        self.assertFalse(get_liza_country_code(False))

    def test_button_shows_for_french_overseas_and_known_liza_country(self):
        P = self.env["res.partner"]
        gp = self.env.ref("base.gp")  # Guadeloupe (French territory)
        de = self.env.ref("base.de")  # Germany (not supported)
        # French company in Guadeloupe, only a registry -> territory maps to FR
        p1 = P.create(
            {
                "name": "GP reg",
                "is_company": True,
                "company_registry": "393788609",
                "country_id": gp.id,
            }
        )
        self.assertTrue(p1.liza_show_button_enhance)
        # Already identified as FR by Liza, no VAT, foreign address -> shows
        p2 = P.create(
            {
                "name": "known FR",
                "is_company": True,
                "company_registry": "12345678",
                "country_id": de.id,
                "liza_country_code": "FR",
            }
        )
        self.assertTrue(p2.liza_show_button_enhance)
        # Registry only + unsupported country, not known to Liza -> hidden
        p3 = P.create(
            {
                "name": "DE reg",
                "is_company": True,
                "company_registry": "12345678",
                "country_id": de.id,
            }
        )
        self.assertFalse(p3.liza_show_button_enhance)

    def test_get_country_code_from_vat(self):
        # Only the allowed uppercase country prefixes are recognised
        self.assertEqual(get_country_code_from_vat("BE0405056855"), "BE")
        self.assertEqual(get_country_code_from_vat("LU26832882"), "LU")
        self.assertEqual(get_country_code_from_vat("NL810433941B01"), "NL")
        self.assertEqual(get_country_code_from_vat("FR76803453802"), "FR")
        # No country prefix / not allowed / empty
        self.assertFalse(get_country_code_from_vat("0405056855"))
        self.assertFalse(get_country_code_from_vat("DE123456789"))
        self.assertFalse(get_country_code_from_vat(""))
        self.assertFalse(get_country_code_from_vat(False))

    def test_get_enable_field(self):
        self.assertEqual(get_enable_field("liza_name"), "liza_name_enable")
        # A trailing '_id' is stripped before adding '_enable'
        self.assertEqual(get_enable_field("liza_prefLang_id"), "liza_prefLang_enable")

    def test_get_service_args_by_vat(self):
        service, args, missing = _liza_get_service_args(vat="BE0405056855")
        self.assertEqual(service, "GetCompanyByVat")
        self.assertEqual(args["VatNumber"], "BE0405056855")
        self.assertEqual(args["CountryCode"], "BE")
        self.assertFalse(missing)

    def test_get_service_args_by_registry(self):
        service, args, missing = _liza_get_service_args(
            registry="0405056855", country_code="BE"
        )
        self.assertEqual(service, "GetCompanyByRegistrationNumber")
        self.assertEqual(args["RegistrationNumber"], "0405056855")
        self.assertEqual(args["CountryCode"], "BE")
        self.assertFalse(missing)

    def test_get_service_args_by_search_prefers_zip_over_city(self):
        service, args, _ = _liza_get_service_args(
            search="ACME", zip="9100", city="Sint-Niklaas", country_code="BE"
        )
        self.assertEqual(service, "SearchCompanies")
        self.assertEqual(args["SearchTerm"], "ACME")
        self.assertEqual(args["PostalCodeOrCityName"], "9100")

    def test_get_service_args_by_search_falls_back_to_city(self):
        _, args, _ = _liza_get_service_args(
            search="ACME", city="Sint-Niklaas", country_code="BE"
        )
        self.assertEqual(args["PostalCodeOrCityName"], "Sint-Niklaas")

    def test_get_service_args_missing_everything(self):
        service, _, missing = _liza_get_service_args()
        self.assertFalse(service)
        self.assertIn("Country", missing)
        self.assertIn("VAT", missing)
        self.assertIn("Company ID", missing)
        self.assertIn("Search Term", missing)

    def test_format_float_value_distinguishes_zero_from_none(self):
        # 0 must stay 0.0 (a disclosed zero), not be turned into None
        self.assertEqual(format_float_value(0), 0.0)
        self.assertEqual(format_float_value("12.5"), 12.5)
        # Undisclosed values collapse to None
        self.assertIsNone(format_float_value(False))
        self.assertIsNone(format_float_value(None))
        self.assertIsNone(format_float_value(""))

    def test_format_date(self):
        self.assertEqual(format_date("20240131").isoformat()[:10], "2024-01-31")
        # Invalid / empty input is returned as False
        self.assertFalse(format_date("not-a-date"))
        self.assertFalse(format_date(False))

    def test_format_industry(self):
        self.assertEqual(
            format_industry({"Code": "23650", "Description": "Fibre cement"}),
            "23650 - Fibre cement",
        )

    def test_format_warnings(self):
        self.assertEqual(
            format_warnings({"string": ["Warning 1", "Warning 2"]}),
            "- Warning 1\n- Warning 2",
        )

    def test_liza_client_sets_recommended_headers(self):
        """liza_client must attach the Api-Client-* headers Liza recommends."""
        with patch("odoo.addons.liza_base.liza_utils.Client") as mock_client:
            liza_client("https://connect.liza.nl/V2.0/alacarteservice.asmx")
        transport = mock_client.call_args.kwargs["transport"]
        headers = transport.session.headers
        self.assertEqual(headers["Api-Client-Name"], "Odoo liza_base")
        # Version comes from the module manifest and must be non-empty
        self.assertTrue(headers["Api-Client-Version"])

    def test_liza_client_retries_transient_gateway_errors(self):
        """Transient gateway errors (502/503/504) must be retried."""
        with patch("odoo.addons.liza_base.liza_utils.Client") as mock_client:
            liza_client("https://connect.liza.nl/V2.0/alacarteservice.asmx")
        session = mock_client.call_args.kwargs["transport"].session
        retry = session.get_adapter("https://connect.liza.nl/").max_retries
        self.assertGreaterEqual(retry.total, 1)
        for status in (502, 503, 504):
            self.assertIn(status, retry.status_forcelist)

    @mute_logger("odoo.addons.liza_base.models.res_partner")
    def test_liza_image_tag(self):
        """The health-barometer HTML tag is built only for existing images."""
        partner = self.env["res.partner"].create({"name": "T", "is_company": True})
        # A barometer image that ships with the module -> an <img> tag
        partner.liza_image = "pos-01.png"
        self.assertIn(
            "liza_base/static/img/liza_barometer/pos-01.png", partner.liza_image_tag
        )
        # A missing file -> no tag (warning branch)
        partner.liza_image = "does-not-exist.png"
        self.assertFalse(partner.liza_image_tag)
        # No image at all -> no tag
        partner.liza_image = False
        self.assertFalse(partner.liza_image_tag)

    @patch("odoo.addons.liza_base.liza_utils.liza_client")
    def test_liza_get_returns_readable_soap_fault(self, mock_liza_client):
        """A SOAP fault becomes status -2 with a readable message instead of a
        raw zeep exception bubbling up as an opaque server error."""
        service = MagicMock(side_effect=Fault("Unknown fault occured"))
        mock_liza_client.return_value.service.Alerts_FetchBulk = service
        status, message = _liza_get(
            "https://connect.liza.nl/V2.0/alacarteservice.asmx",
            "Alerts_FetchBulk",
            "login",
            "password",
            "NL",
            {},
        )
        self.assertEqual(status, -2)
        self.assertIn("Unknown fault occured", message)

    def test_format_liza_fault_includes_code_and_detail(self):
        """A production fault carries a code and a detail body; both must end up
        in the message so the user sees why Liza refused the call."""
        detail = etree.fromstring("<detail><Reason>Quota exceeded</Reason></detail>")
        fault = Fault("Request rejected", code="soap:Client", detail=detail)
        message = _format_liza_fault(fault)
        self.assertIn("Request rejected", message)
        self.assertIn("soap:Client", message)
        self.assertIn("Quota exceeded", message)
        # A bare fault degrades to a readable message instead of an empty string
        self.assertEqual(_format_liza_fault(Fault(None)), "Unknown SOAP fault")

    @patch("odoo.addons.liza_base.liza_utils.liza_client")
    def test_liza_get_returns_readable_connection_error(self, mock_liza_client):
        """A network failure must surface as status -2 with a readable message,
        the same way a SOAP fault does, instead of a raw requests exception."""
        service = MagicMock(side_effect=RequestsConnectionError("connection refused"))
        mock_liza_client.return_value.service.GetCompanyByVat = service
        status, message = _liza_get(
            "https://connect.liza.nl/V2.0/alacarteservice.asmx",
            "GetCompanyByVat",
            "login",
            "password",
            "NL",
            {},
        )
        self.assertEqual(status, -2)
        self.assertIn("Liza connection error", message)
        self.assertIn("connection refused", message)

    @patch("odoo.addons.liza_base.liza_utils.liza_client")
    def test_liza_get_returns_readable_transport_error(self, mock_liza_client):
        service = MagicMock(side_effect=TransportError("503 Service Unavailable"))
        mock_liza_client.return_value.service.GetCompanyByVat = service
        status, message = _liza_get(
            "https://connect.liza.nl/V2.0/alacarteservice.asmx",
            "GetCompanyByVat",
            "login",
            "password",
            "NL",
            {},
        )
        self.assertEqual(status, -2)
        self.assertIn("Liza connection error", message)

    def test_get_balance_values_resets_fields_when_balance_disabled(self):
        """When Liza discloses no balance data, every balance field must be
        cleared. Leaving them untouched would keep last year's figures on the
        contact after a refresh."""
        values = get_balance_values({"Balances": {"IsEnabled": False, "Value": None}})
        self.assertFalse(values["liza_balance_data_enable"])
        for field in BALANCE_FIELDS + BALANCE_NESTED_FIELDS:
            self.assertFalse(values[field], f"{field} should be reset to False")

    def test_get_balance_values_reads_figures_from_nested_balance_data(self):
        """The financial figures sit one level deeper than the fiscal year."""
        values = get_balance_values(
            {
                "Balances": {
                    "IsEnabled": True,
                    "Value": {
                        "Balance": [
                            {
                                "FiscalYear": "2025",
                                "Currency": "EUR",
                                "ToDate": "20251231",
                                "BalanceData": {
                                    "BalanceData": [
                                        {"Key": "UNIFIED_Equity", "Value": "1000.5"},
                                        {"Key": "UNIFIED_Turnover", "Value": "2000"},
                                        {"Key": "UNIFIED_Employees", "Value": "10"},
                                        {"Key": "UNIFIED_ProfitLoss", "Value": "-50"},
                                        {"Key": "UNIFIED_GrossMargin", "Value": "300"},
                                    ]
                                },
                            }
                        ]
                    },
                }
            }
        )
        self.assertTrue(values["liza_balance_data_enable"])
        self.assertEqual(values["liza_balance_year"], "2025")
        self.assertEqual(values["liza_equityCapital"], "1000.5")
        self.assertEqual(values["liza_addedValue"], "-50")

    def test_get_balance_values_without_nested_figures(self):
        """A balance that discloses a fiscal year but no figures yields no
        amounts at all. Note the keys are absent rather than False, so a write()
        of these values leaves whatever the contact already had."""
        values = get_balance_values(
            {
                "Balances": {
                    "IsEnabled": True,
                    "Value": {
                        "Balance": [
                            {
                                "FiscalYear": "2025",
                                "Currency": "EUR",
                                "ToDate": "20251231",
                                "BalanceData": None,
                            }
                        ]
                    },
                }
            }
        )
        self.assertEqual(values["liza_balance_year"], "2025")
        for field in BALANCE_NESTED_FIELDS:
            self.assertNotIn(field, values)
