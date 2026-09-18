# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime
from uuid import uuid4

from odoo import api, exceptions, fields, models, tools

from ..liza_const import (
    ADDRESS_FIELDS,
    ALLOWED_COUNTRY_CODES,
    DATE_FIELDS,
    FILL_FIELD_MAP,
    FLOAT_FIELDS,
)
from ..liza_format import (
    format_date,
    format_float_value,
    format_industry,
    format_liable_party,
    format_warnings,
    get_country_id,
    get_currency_id,
    get_lang_id,
)
from ..liza_utils import (
    get_all_enable_fields,
    get_balance_values,
    get_country_code_from_vat,
    get_data_values,
    get_liza_country_code,
    get_nested_values,
    liza_get,
    liza_push,
    liza_sync,
)

LIZA_FIELD_ARGS = {"readonly": True, "copy": False}
LIZA_SYNC_STATUS_NONE = "none"
LIZA_SYNC_STATUS_PENDING = "pending"
LIZA_SYNC_STATUS_ACTIVE = "active"

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    # System data
    liza_lastupdate = fields.Datetime("Last Update", **LIZA_FIELD_ARGS)
    liza_error = fields.Char("Error", help="Error when enhancing contact with Liza")

    # Liza main data fields (in main response of API, comes with _enable field)
    liza_name_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_name = fields.Char(
        **LIZA_FIELD_ARGS,
        help="The official company name, for example 'Nationale Maatschappij Der "
        "Belgisch Spoorwegen' or 'Plopsa'.",
    )
    liza_commercial_name_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_commercial_name = fields.Char(
        **LIZA_FIELD_ARGS,
        help="Commercial company name, for example 'Plopsa Coo'",
    )
    liza_jur_form_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_jur_form = fields.Char(
        "Legal Form",
        **LIZA_FIELD_ARGS,
        help="Legal form of the company, such as 'NV', 'SA', 'NP' etc.",
    )
    liza_vat_liable_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_vat_liable = fields.Boolean(
        "Subject to VAT",
        **LIZA_FIELD_ARGS,
        help="Is the company subject to VAT or not",
    )
    liza_vat_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_vat = fields.Char(
        "Liza VAT",
        **LIZA_FIELD_ARGS,
        help="Company VAT number",
    )
    liza_prefLang_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_prefLang_id = fields.Many2one(
        "res.lang",
        string="Preferred Language",
        **LIZA_FIELD_ARGS,
        help="Preferred languages for communication, based on publication languages, "
        "among other factors.",
    )
    liza_registry_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_registry = fields.Char(
        "Company Registry",
        **LIZA_FIELD_ARGS,
        help="The official registration number of a company. \n"
        "• Belgium: KBO, BCE, CBE\n"
        "• Netherlands: KvK\n"
        "• Luxembourg: RCS\n"
        "• France: SIREN",
    )
    liza_country_code_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_country_code = fields.Char(
        **LIZA_FIELD_ARGS,
        help="The official code of Belgium, The Netherlands, Luxembourg and France",
    )
    liza_main_industry_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_main_industry = fields.Char(
        "Main Industry",
        **LIZA_FIELD_ARGS,
        help="The main activity of this company (NACE)",
    )
    liza_industries_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_industries = fields.Text(
        "Other Activities",
        **LIZA_FIELD_ARGS,
        help="A list of the declared activities (NACE)",
    )
    liza_email_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_email = fields.Char(**LIZA_FIELD_ARGS)
    liza_website_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_website = fields.Char(**LIZA_FIELD_ARGS)
    liza_phone_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_phone = fields.Char(**LIZA_FIELD_ARGS)
    liza_peppol_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_peppol = fields.Boolean(
        "Registered on Peppol",
        **LIZA_FIELD_ARGS,
        help="A PEPPOL ID is a unique identification code used within the PEPPOL "
        "network for electronic communication, enabling standardized invoicing, "
        "ordering, and reporting in compliance with EU regulations.",
    )
    liza_sync_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_sync = fields.Boolean(
        "In Alerts",
        **LIZA_FIELD_ARGS,
        help="Partner is being synchronized with Liza. To remove from alerts, "
        "please contact Liza.",
    )
    liza_sync_reference = fields.Char(
        **LIZA_FIELD_ARGS,
        index="btree_not_null",
        help="Identifies the record from Odoo with the one saved in the Alerts list at "
        "Liza",
    )

    # NL specific fields
    liza_rsin_number_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_rsin_number = fields.Char(
        "Liza RSIN",
        **LIZA_FIELD_ARGS,
        help="RSIN: 'Rechtspersonen en Samenwerkingsverbanden "
        "Informatienummer' is used to exchange data with other government "
        "organisations, such as the Netherlands Tax Administration. "
        "(Netherlands only)",
    )
    liza_liable_party_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_liable_party = fields.Text(
        "Liable Party",
        **LIZA_FIELD_ARGS,
        help="A 403 declaration is a liability statement in which the parent company "
        "accepts joint and several liability for the debts of its subsidiary. "
        "As a result, the subsidiary is not required; to publish its own annual "
        "accounts its figures are included in the consolidated financial "
        "statements of the parent company. (Netherlands only)",
    )

    # Liza nested data fields (nested in a main data field of the response)
    liza_currency_id = fields.Many2one(
        "res.currency", "Liza Currency", **LIZA_FIELD_ARGS
    )

    # Companystatus
    liza_companystatus_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_companystatus = fields.Char(
        "Liza Status",
        **LIZA_FIELD_ARGS,
        help="Whether a company is active or not",
    )
    liza_companystatus_code = fields.Char("Liza Company StatusCode", **LIZA_FIELD_ARGS)

    # Address
    liza_address_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_street = fields.Char(
        **LIZA_FIELD_ARGS,
        help="Address of the registered office or headquarters",
    )
    liza_zip = fields.Char("Liza Postal code", **LIZA_FIELD_ARGS)
    liza_city = fields.Char(**LIZA_FIELD_ARGS)
    liza_country_code_address = fields.Char("Address Country Code", **LIZA_FIELD_ARGS)
    liza_country_id = fields.Many2one("res.country", "Liza Country", **LIZA_FIELD_ARGS)

    # Credit limit
    liza_creditLimit_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_creditLimit = fields.Monetary(
        "Liza Credit Limit", currency_field="liza_currency_id", **LIZA_FIELD_ARGS
    )
    liza_creditLimit_unset = fields.Boolean(
        "Liza Credit Limit Unset", **LIZA_FIELD_ARGS
    )
    liza_creditLimit_info = fields.Char("Credit Limit Info", **LIZA_FIELD_ARGS)
    liza_warnings_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_warnings = fields.Text(
        "Warnings",
        **LIZA_FIELD_ARGS,
        help="Financial warning signs about the company",
    )

    # Balance
    liza_startDate_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_startDate = fields.Date(
        "Established", **LIZA_FIELD_ARGS, help="Date of establishment of the company"
    )
    liza_endDate_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_endDate = fields.Date(
        "End Date",
        **LIZA_FIELD_ARGS,
        help="Date at which the company stopped its activity",
    )
    liza_score_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_score = fields.Char(
        **LIZA_FIELD_ARGS,
        help="The Liza health barometer",
    )
    liza_image = fields.Char("Liza Barometer Image", **LIZA_FIELD_ARGS)
    liza_balance_data_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_balance_year = fields.Char("Book Year", **LIZA_FIELD_ARGS)
    liza_closed_date = fields.Date("To Date", **LIZA_FIELD_ARGS)
    liza_equityCapital = fields.Float("Equity", **LIZA_FIELD_ARGS)
    liza_equityCapital_unset = fields.Boolean(
        "Liza Equity Capital Unset", **LIZA_FIELD_ARGS
    )
    liza_average_fte = fields.Float("Average number of staff in FTE", **LIZA_FIELD_ARGS)
    liza_average_fte_unset = fields.Boolean(
        "Liza Average number of staff in FTE Unset", **LIZA_FIELD_ARGS
    )
    liza_addedValue = fields.Float("Profit/Loss of the Book Year", **LIZA_FIELD_ARGS)
    liza_addedValue_unset = fields.Boolean(
        "Liza Gross Margin (+/-) Unset", **LIZA_FIELD_ARGS
    )
    liza_turnover = fields.Float("Turnover", **LIZA_FIELD_ARGS)
    liza_turnover_unset = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_result = fields.Float("Gross Margin", **LIZA_FIELD_ARGS)
    liza_result_unset = fields.Boolean("Gross Margin Unset", **LIZA_FIELD_ARGS)

    # Reports
    liza_url_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_url = fields.Char(
        "Details",
        **LIZA_FIELD_ARGS,
        help="Further details about this company on liza.nl",
    )
    liza_url_report_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_url_report = fields.Char(
        "Commercial Report",
        **LIZA_FIELD_ARGS,
        help="Detailed report about this company on liza.nl",
    )
    liza_url_payment_experience_enable = fields.Boolean(**LIZA_FIELD_ARGS)
    liza_url_payment_experience = fields.Char(
        "Payment Experience",
        **LIZA_FIELD_ARGS,
        help="A link to the payment experience report on liza.nl",
    )

    # Helper fields
    liza_show_button_address = fields.Boolean(
        "Liza Button Address Enabled", compute="_compute_liza_show_button_address"
    )
    liza_show_tab = fields.Boolean(
        "Liza Tab Enabled", compute="_compute_liza_liza_show_tab"
    )
    liza_show_button_enhance = fields.Boolean(
        "Liza Button Enhance Enabled", compute="_compute_liza_show_button_enhance"
    )
    liza_image_tag = fields.Html(
        "Health Barometer",
        compute="_compute_liza_image_tag",
    )

    # Config fields
    liza_followup_enable = fields.Boolean(compute="_compute_liza_followup_enable")
    liza_sync_status = fields.Selection(
        [
            (LIZA_SYNC_STATUS_NONE, "None"),
            (LIZA_SYNC_STATUS_PENDING, "Pending"),
            (LIZA_SYNC_STATUS_ACTIVE, "Active"),
        ],
        "Alert Status",
        default=LIZA_SYNC_STATUS_NONE,
        readonly=True,
        copy=False,
    )

    @api.depends_context("company")
    @api.depends("company_id")
    def _compute_liza_followup_enable(self):
        env_company = self.env.company
        for partner in self:
            company = partner.company_id or env_company
            partner.liza_followup_enable = company.liza_followup_enable

    @api.depends("is_company", "vat", "country_id", "liza_country_code")
    def _compute_liza_show_button_enhance(self):
        """
        Show the button for a company when its country can be resolved to a
        Liza-supported one: an already known Liza country, a VAT with a valid
        country prefix, or an address country (French overseas territories count
        as FR). With no country at all the user can still search.
        """
        for rec in self:
            rec.liza_show_button_enhance = bool(
                rec.is_company
                and (
                    not rec.country_id
                    or rec.liza_country_code in ALLOWED_COUNTRY_CODES
                    or (rec.vat and get_country_code_from_vat(rec.vat))
                    or get_liza_country_code(rec.country_id.code)
                    in ALLOWED_COUNTRY_CODES
                )
            )

    @api.depends("liza_image")
    def _compute_liza_image_tag(self):
        for rec in self:
            liza_image_tag = None
            if rec.liza_image:
                path = f"liza_base/static/img/liza_barometer/{rec.liza_image}"
                try:
                    tools.misc.file_path(path)
                    liza_image_tag = f'<img class="img-fluid" src="/{path}"/>'
                except FileNotFoundError:
                    _logger.warning("File not found: %s", path)
                    self.env["ir.logging"].sudo().create(
                        {
                            "name": _logger.name,
                            "type": "server",
                            "level": "WARNING",
                            "message": f"File not found: {path}",
                            "path": __name__,
                            "func": "_compute_liza_image_tag",
                            "line": 0,
                        }
                    )
            rec.liza_image_tag = liza_image_tag

    @api.depends(*ADDRESS_FIELDS)
    def _compute_liza_show_button_address(self):
        """for the button to be shown
        the partner has to have liza_address enabled and data for the address field"""
        for rec in self:
            rec.liza_show_button_address = all(rec[field] for field in ADDRESS_FIELDS)

    @api.depends(*get_all_enable_fields())
    def _compute_liza_liza_show_tab(self):
        """
        Show liza tab if there's an error message or any of the enable fields is True
        """
        for rec in self:
            rec.liza_show_tab = rec.liza_error or any(
                rec[enable_field] for enable_field in get_all_enable_fields()
            )

    def _liza_format(self, values):
        """
        In-place formatting of specific dict and M2O in values
        """
        # Transform values to M2O IDs
        values["liza_prefLang_id"] = (
            lang_code := values.get("liza_prefLang_id")
        ) and get_lang_id(self.env, lang_code)
        values["liza_country_id"] = (
            country_code_address := values.get("liza_country_code_address")
        ) and get_country_id(self.env, country_code_address)
        values["liza_currency_id"] = (
            currency_name := values.get("liza_currency_id")
        ) and get_currency_id(self.env, currency_name)

        # Transform Text and HTML
        values["liza_warnings"] = (
            warnings := values.get("liza_warnings")
        ) and format_warnings(warnings)
        values["liza_main_industry"] = (
            main_industry := values.get("liza_main_industry")
        ) and format_industry(main_industry)
        values["liza_industries"] = (
            industries := values.get("liza_industries")
        ) and "\n".join(format_industry(industry) for industry in industries)
        values["liza_liable_party"] = (
            liable_party_dict := values.get("liza_liable_party")
        ) and format_liable_party(liable_party_dict, self.env)
        values["liza_peppol"] = bool(values["liza_peppol"])

        # Transform Dates
        for field in DATE_FIELDS:
            values[field] = format_date(values[field])

        # Format floats and flag as set or unset
        for float_field in FLOAT_FIELDS:
            if float_field in values:
                value = format_float_value(values[float_field])
                values[float_field] = value
                values[f"{float_field}_unset"] = value is None

        return values

    def _liza_parse(self, liza_response):
        """
        Parse liza data to odoo-field values
        """
        values = {
            "liza_lastupdate": datetime.now(),
            **get_data_values(liza_response),
            **get_nested_values(liza_response),
            **get_balance_values(liza_response),
        }
        values = self._liza_format(values)
        return values

    def _liza_populate(self, liza_response):
        """
        Fill liza fields
        """
        self.ensure_one()
        values = self._liza_parse(liza_response)
        if "liza_sync" in values:
            if values.get("liza_sync"):
                values["liza_sync_status"] = LIZA_SYNC_STATUS_ACTIVE
            elif self.liza_sync_status == LIZA_SYNC_STATUS_ACTIVE:
                # No longer in Alerts: stop tracking it.
                values["liza_sync_status"] = LIZA_SYNC_STATUS_NONE
        self.write(values)

    def _get_liza_credentials(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        url = IrConfigParameter.get_param("liza.alacarte", "")

        if "V2.0" not in url:
            raise exceptions.ValidationError(
                self.env._("Liza: Please use the address for API V2.0"),
            )

        login = self.env.company.liza_login
        password = self.env.company.liza_password
        lang = self.env.context.get("lang", self.env.user.lang)[:2].upper()
        if lang not in ["FR", "NL"]:
            lang = "EN"
        return url, login, password, lang

    def _liza_call_get(self, args):
        """
        Raises:
            - Access error
        Returns:
            - Error
            - Search results
        """
        if not self.env.user.has_group("liza_base.liza_download"):
            raise exceptions.AccessDenied(
                self.env._("Liza: You don't have access to download data")
            )
        error = ""
        url, login, password, lang = self._get_liza_credentials()
        status, liza_response = liza_get(url, login, password, lang, args)
        if status == -1:
            error = self.env._(
                "Missing values for company search: %(message)s",
                message=liza_response,
            )
        elif status != 0:
            error = self.env._(
                "Liza status %(status)i: %(message)s",
                status=status,
                message=liza_response,
            )
        return error, liza_response

    def _liza_enhance(self):
        errors = []
        for partner in self:
            args = {}
            if partner.vat:
                args["vat"] = partner.vat
            if partner.company_registry:
                args["registry"] = partner.company_registry
            country_code = (
                partner.liza_country_code
                or get_country_code_from_vat(partner.vat)
                or get_liza_country_code(partner.country_id.code)
            )
            if country_code:
                if country_code not in ALLOWED_COUNTRY_CODES:
                    errors.append(
                        self.env._(
                            "Liza only supports companies based in %(country_codes)s",
                            country_codes=ALLOWED_COUNTRY_CODES,
                        )
                    )
                    continue
                args["country_code"] = country_code

            error, liza_response = self._liza_call_get(args)

            if error:
                partner.liza_error = error
                errors.append(error)
            else:
                partner.liza_error = False
                partner._liza_populate(liza_response)
        return errors

    def _liza_copy_address(self):
        if not self.env.user.has_group("liza_base.liza_view"):
            raise exceptions.AccessDenied(self.env._("Liza: You don't have access"))
        env_company = self.env.company
        for partner in self:
            company = partner.company_id or env_company
            for liza_field, odoo_field in FILL_FIELD_MAP.items():
                if not company[f"fill_{liza_field}"]:
                    continue
                value = partner[liza_field]
                # Never wipe an existing identifier when Liza returned nothing
                # for it: only overwrite the VAT or registration number when we
                # actually have a value.
                if odoo_field in ("vat", "company_registry") and not value:
                    continue
                partner[odoo_field] = value
            partner.street2 = None
            partner.state_id = None

    @api.model
    def _liza_ensure_credentials(self):
        return bool(self.env.company.liza_login and self.env.company.liza_password)

    def liza_button_enhance(self):
        """
        Populate liza fields from Liza
        """
        self.ensure_one()
        if not self.env.user.has_group("liza_base.liza_download"):
            raise exceptions.AccessDenied(
                self.env._("Liza: You don't have access to download data")
            )
        if not self._liza_ensure_credentials():
            return self._liza_call_wizard_credentials()
        if not self.vat and not self.company_registry:
            return self._liza_call_wizard_search()

        errors = self._liza_enhance()
        if errors:
            msg = (
                errors[0]
                if len(errors) == 1
                else "\n".join(f"- {error}" for error in errors)
            )
            self.liza_error = msg
            raise exceptions.ValidationError(msg)
        self.liza_error = False
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": self.env._("Successfully fetched Liza data"),
                "sticky": False,
                "next": {
                    "type": "ir.actions.client",
                    "tag": "soft_reload",
                },
            },
        }

    def liza_button_copy_address(self):
        """
        Copy Liza data to res.partner fields
        """
        self.ensure_one()
        self._liza_copy_address()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": self.env._("Copied Liza data to Contact"),
                "sticky": False,
                "next": {
                    "type": "ir.actions.client",
                    "tag": "soft_reload",
                },
            },
        }

    def _liza_call_wizard_search(self):
        self.ensure_one()
        # Pass partner in context to trigger default_get and populate search terms
        wizard = (
            self.env["liza.search.wizard"]
            .with_context(default_partner_id=self.id)
            .create({})
        )
        # Do initial search
        return wizard.liza_search()

    @api.model
    def _liza_call_wizard_credentials(self):
        self.ensure_one()
        wizard_form = self.env.ref("liza_base.liza_credential_wizard")
        return {
            "name": "Enter Liza Credentials",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "liza_base.credential_wizard_base",
            "view_id": wizard_form.id,
            "target": "new",
            "context": self.env.context,
        }

    def _push_followup_partners(self, partner_list):
        error = ""
        args = [{"AlertCompany": partner_list}]
        url, login, password, lang = self._get_liza_credentials()
        status, liza_response = liza_push(url, login, password, lang, args)
        if status != 0:
            liza_error = self.env._(
                "Liza error %(status)i: %(message)s",
                status=status,
                message=liza_response,
            )
            return liza_error, [], 0
        error_partners = (liza_response.get("InvalidCompanies", {}) or {}).get(
            "InvalidAlertCompany", []
        )
        error_partner_dicts = [
            {
                "liza_sync_reference": errp.get("Company", {}).get("Reference", False),
                "msg": errp.get("Message", ""),
            }
            for errp in error_partners
        ]
        num_partner_updated = liza_response["NumberOfAlertsAddedOrUpdated"]
        return error, error_partner_dicts, num_partner_updated

    def action_push_followup_partners(self):
        """
        Add partners in self to a monitor-list on liza side.
        Changes to the list take effect the next day.
        1. Check partners have at least country and (vat or registry)
        2. Collect erroneous partners and leave error message on record
        3. Push valid partners
        4. Return notification for success and error
        5. If error, redirect to view of erroneous partners
        Raise:
            - Missing credentials
            - Liza error
        Return:
            - Notification
            - View action if errors
        """
        if not self._liza_ensure_credentials():
            raise exceptions.ValidationError(
                self.env._(
                    "Missing Liza credentials on company %(company)s",
                    company=self.env.company.name,
                )
            )
        partner_errors = self.env["res.partner"]
        partner_list = []
        for partner in self:
            vat = partner.vat or partner.liza_vat
            registry = partner.company_registry or partner.liza_registry
            country_code = (
                partner.liza_country_code
                or get_country_code_from_vat(vat)
                or get_liza_country_code(partner.country_id.code)
            )
            if not (vat or registry):
                partner.liza_error = self.env._("Missing VAT or Company Registry.")
                partner_errors |= partner
            elif not country_code:
                partner.liza_error = self.env._("Missing country.")
                partner_errors |= partner
            elif country_code not in ALLOWED_COUNTRY_CODES:
                partner.liza_error = self.env._(
                    "Invalid country. Countries supported: %(countries)s.",
                    countries=ALLOWED_COUNTRY_CODES,
                )
                partner_errors |= partner
            else:
                partner.liza_error = False
                if not partner.liza_sync_reference:
                    # Unique identifier to store on Liza side
                    partner.liza_sync_reference = str(uuid4())
                partner_list.append(
                    {
                        "CountryCode": country_code,
                        "Identifier": vat or registry,
                        "IdentifierType": "VatNumber" if vat else "RegistrationNumber",
                        "Reference": partner.liza_sync_reference,
                    }
                )

        liza_error, error_partner_dicts, num_partner_updated = (
            self._push_followup_partners(partner_list)
        )
        if liza_error:
            raise exceptions.ValidationError(liza_error)
        for partner_dict in error_partner_dicts:
            if ref := partner_dict.get("liza_sync_reference"):
                partner = self.search([("liza_sync_reference", "=", ref)], limit=1)
                partner.liza_error = partner_dict.get("msg")
                partner_errors |= partner

        msg = ""
        msg_append = self.env._(" to Liza Alerts.")
        if num_partner_updated:
            msg = self.env._(
                "Added %(num_partner)i contact(s)", num_partner=num_partner_updated
            )
        for success_partner in self - partner_errors:
            success_partner.liza_sync_status = LIZA_SYNC_STATUS_PENDING
        if partner_errors:
            if msg:
                msg += ". "
            msg += self.env._(
                "Failed to push %(num_partner_errors)i contact(s)",
                num_partner_errors=len(partner_errors),
            )
            action = partner_errors._get_records_action()
            action["name"] = "Failed contacts"
            params = {
                "type": "danger",
                "message": msg + msg_append,
                "sticky": True,
                "next": action,
            }
        else:
            params = {
                "type": "success",
                "message": msg + msg_append,
                "sticky": False,
                "next": {
                    "type": "ir.actions.client",
                    "tag": "soft_reload",
                },
            }
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": params,
        }

    @api.model
    def _liza_find_followup_partner(self, reference, values):
        """Find the contact a followup record refers to.

        Match on the follow-up reference we stored when pushing the contact.
        Fall back to the Liza registration number and country, because a record
        removed from Alerts may no longer carry its follow-up reference.
        """
        Partner = self.env["res.partner"]
        if reference:
            partner = Partner.search([("liza_sync_reference", "=", reference)], limit=1)
            if partner:
                return partner
        registry = values.get("liza_registry")
        country = values.get("liza_country_code")
        if registry and country:
            return Partner.search(
                [
                    ("liza_registry", "=", registry),
                    ("liza_country_code", "=", country),
                ],
                limit=1,
            )
        return Partner

    @api.model
    def _cron_liza_followup(self):
        """
        Cron to catch any data that has changed on partners on the monitor-list
        -> Call for updated companies
        <- Receive companies and update them in Odoo
        -> Call for more companies and simultaneously confirm the companies received
            in last call
        ...
        1. Get updates from liza
        2. Update Odoo
        3. Confirm updates to liza (done in next call)
        4. If more updates remaining, repeat
        """
        Partner = self.env["res.partner"]
        if not self._liza_ensure_credentials():
            raise exceptions.ValidationError(
                self.env._(
                    "Missing liza credentials on company %(company)s",
                    company=self.env.company.name,
                )
            )
        url, login, password, lang = self._get_liza_credentials()
        updated_partners = []
        is_first_call = True
        while is_first_call or updated_partners:
            is_first_call = False
            status, liza_response = liza_sync(
                url, login, password, lang, updated_partners
            )
            if status != 0:
                raise exceptions.ValidationError(
                    self.env._(
                        "Liza error %(status)i while syncing: %(message)s",
                        status=status,
                        message=liza_response,
                    )
                )
            remaining = (liza_response.get("RemainingChanges", {}) or {}).get(
                "RemainingChangesCount", 0
            )
            partner_datas = (liza_response["CompanyResponses"] or {}).get(
                "CompanyResponseV2_0", []
            )
            _logger.info(
                "Liza: Received %i contact(s) to update. Remaining: %i.",
                len(partner_datas),
                remaining,
            )
            self.env["ir.logging"].sudo().create(
                {
                    "name": _logger.name,
                    "type": "server",
                    "level": "INFO",
                    "message": (
                        f"Liza: Received {len(partner_datas)}"
                        f" contact(s) to update. Remaining: {remaining}."
                    ),
                    "path": __name__,
                    "func": "_cron_liza_followup",
                    "line": 0,
                }
            )

            updated_partners = []
            updated_existing_partners = []
            for partner_data in partner_datas:
                liza_sync_reference = (
                    partner_data.get("FollowUpReference", {}) or {}
                ).get("Value", False)
                # Isolate each contact in its own savepoint: a single badly
                # structured record must not roll back or block the rest of the
                # batch. A broad except is intentional here — the payload comes
                # from an external service and any parsing/write error on one
                # record should only skip that record.
                try:
                    with self.env.cr.savepoint():
                        values = Partner._liza_parse(partner_data)
                        partner = self._liza_find_followup_partner(
                            liza_sync_reference, values
                        )
                        if partner:
                            if values.get("liza_sync"):
                                values["liza_sync_status"] = LIZA_SYNC_STATUS_ACTIVE
                            elif partner.liza_sync_status == LIZA_SYNC_STATUS_ACTIVE:
                                # Removed from Alerts: stop tracking it.
                                values["liza_sync_status"] = LIZA_SYNC_STATUS_NONE
                            partner.write(values)
                            # Only re-sync the contact fields while the company is
                            # actively tracked, so a removal never blanks the
                            # contact with empty data.
                            if values.get("liza_sync"):
                                partner._liza_copy_address()
                            updated_existing_partners.append(partner.id)

                        # Confirm we treated this record (even if no longer in
                        # DB) so it is removed from the update list. Sent to Liza
                        # as confirmed in the next call.
                        updated_partners.append(
                            {
                                "CountryCode": values.get("liza_country_code"),
                                "RegistrationNumber": values.get("liza_registry"),
                            }
                        )
                except Exception as error:
                    _logger.exception(
                        "Liza: Skipping a contact update that could not be "
                        "processed (reference %s)",
                        liza_sync_reference,
                    )
                    self.env["ir.logging"].sudo().create(
                        {
                            "name": _logger.name,
                            "type": "server",
                            "level": "WARNING",
                            "message": (
                                f"Liza: Skipped a contact update that could not "
                                f"be processed (reference {liza_sync_reference}): "
                                f"{error}"
                            ),
                            "path": __name__,
                            "func": "_cron_liza_followup",
                            "line": 0,
                        }
                    )
            if updated_existing_partners:
                _logger.info(
                    "Liza: Updated partners with IDs %s",
                    updated_existing_partners,
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "INFO",
                        "message": (
                            f"Liza: Updated partners with IDs"
                            f" {updated_existing_partners}"
                        ),
                        "path": __name__,
                        "func": "_cron_liza_followup",
                        "line": 0,
                    }
                )
            else:
                _logger.info("Liza: No matching partners found")
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "INFO",
                        "message": "Liza: No matching partners found",
                        "path": __name__,
                        "func": "_cron_liza_followup",
                        "line": 0,
                    }
                )
            # Persist each batch before fetching the next. Confirmations to Liza
            # are irreversible: without an intermediate commit, a fault on a
            # later batch would roll back all enrichments of this run while Liza
            # has already advanced its change queue, leaving contacts confirmed
            # on Liza but never enriched in Odoo. Skipped under tests, where
            # committing a cursor is forbidden.
            if not tools.config["test_enable"]:
                self.env.cr.commit()  # pylint: disable=invalid-commit
