# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# Constant values that are defined by Liza and vary by API versions

# Liza is ok with those keys being visible on Github
SERVICE_INTEGRATOR_ID = "odoo"
SERVICE_INTEGRATOR_SECRET = "1f7f2717-6047-49c2-a69c-b6289aa0e035"
COUNTRY_CODE_BELGIUM = "BE"
COUNTRY_CODE_NETHERLANDS = "NL"
COUNTRY_CODE_LUXEMBOURG = "LU"
COUNTRY_CODE_FRANCE = "FR"
ALLOWED_COUNTRY_SELECTION = [
    (COUNTRY_CODE_BELGIUM, "Belgium"),
    (COUNTRY_CODE_FRANCE, "France"),
    (COUNTRY_CODE_LUXEMBOURG, "Luxembourg"),
    (COUNTRY_CODE_NETHERLANDS, "Netherlands"),
]
ALLOWED_COUNTRY_CODES = (
    COUNTRY_CODE_BELGIUM,
    COUNTRY_CODE_FRANCE,
    COUNTRY_CODE_LUXEMBOURG,
    COUNTRY_CODE_NETHERLANDS,
)
# French overseas territories that belong to the French company registry
# (SIRENE) and VAT system. A company based there (e.g. Guadeloupe) is a French
# company for Liza, so its country code is treated as FR.
FRENCH_REGISTRY_TERRITORY_CODES = (
    "GP",  # Guadeloupe
    "MQ",  # Martinique
    "GF",  # French Guiana
    "RE",  # Réunion
    "YT",  # Mayotte
    "BL",  # Saint-Barthélemy
    "MF",  # Saint-Martin
    "PM",  # Saint-Pierre-et-Miquelon
)
SYNC_PAGE_SIZE = 50  # 1-100; kept below the max for lighter followup calls
DATE_FORMAT = "%Y%m%d"
HASH_ENCODING = "utf-8"

# ODOO FIELDS
# Fields where the value is in the main response.
# Each comes with a corresponding <field_name>_enable field
DATA_FIELDS = [
    "liza_name",
    "liza_commercial_name",
    "liza_vat_liable",
    "liza_vat",
    "liza_email",
    "liza_website",
    "liza_phone",
    "liza_url",
    "liza_url_report",
    "liza_startDate",
    "liza_endDate",
    "liza_registry",
    "liza_rsin_number",
    "liza_sync",
    "liza_main_industry",
    "liza_peppol",
    "liza_country_code",
]
# Fields where the value is nested within other keys
NESTED_FIELDS = {
    "liza_jur_form": ["liza_jur_form"],
    "liza_companystatus": ["liza_companystatus", "liza_companystatus_code"],
    "liza_prefLang_id": ["liza_prefLang_id"],
    "liza_address": [
        "liza_street",
        "liza_zip",
        "liza_city",
        "liza_country_code_address",
    ],
    "liza_score": ["liza_score", "liza_image"],
    "liza_creditLimit": ["liza_creditLimit", "liza_creditLimit_info"],
    "liza_warnings": ["liza_warnings"],
    "liza_industries": ["liza_industries"],
    "liza_liable_party": ["liza_liable_party"],
    "liza_url_payment_experience": ["liza_url_payment_experience"],
}
ADDRESS_FIELDS = [
    "liza_address_enable",
    "liza_street",
    "liza_zip",
    "liza_city",
    "liza_country_id",
]
BALANCE_FIELDS = [
    "liza_currency_id",
    "liza_closed_date",
    "liza_balance_year",
]
BALANCE_NESTED_FIELDS = [
    "liza_equityCapital",
    "liza_turnover",
    "liza_average_fte",
    "liza_addedValue",
    "liza_result",
]
FLOAT_FIELDS = [
    "liza_equityCapital",
    "liza_turnover",
    "liza_average_fte",
    "liza_addedValue",
    "liza_result",
    "liza_creditLimit",
]
DATE_FIELDS = [
    "liza_closed_date",
    "liza_startDate",
    "liza_endDate",
]
# Each key requires a config field 'fill_<field_name>' on company
FILL_FIELD_MAP = {
    "liza_name": "name",
    "liza_commercial_name": "company_name",
    "liza_street": "street",
    "liza_zip": "zip",
    "liza_city": "city",
    "liza_country_id": "country_id",
    "liza_email": "email",
    "liza_website": "website",
    "liza_phone": "phone",
    "liza_vat": "vat",
    "liza_registry": "company_registry",
}

# LIZA API DATA KEYS
DATA_KEYS = {
    "liza_name": "CompanyName",
    "liza_commercial_name": "CommercialName",
    "liza_jur_form": "LegalForm",
    "liza_vat_liable": "VatEnabled",
    "liza_url": "DetailUrl",
    "liza_url_report": "ReportUrl",
    "liza_companystatus": "CompanyStatus",
    "liza_prefLang_id": "PreferredLanguages",
    "liza_address": "Address",
    "liza_balance_data": "Balances",
    "liza_startDate": "StartDate",
    "liza_endDate": "EndDate",
    "liza_score": "Score",
    "liza_creditLimit": "CreditLimit",
    "liza_warnings": "WarningsOverview",
    "liza_registry": "RegistrationNumber",
    "liza_main_industry": "MainActivity",
    "liza_industries": "Activities",
    "liza_email": "EmailAddress",
    "liza_website": "Website",
    "liza_vat": "VatNumber",
    "liza_phone": "TelephoneNumber",
    "liza_rsin_number": "RsinNumber",
    "liza_sync": "IsInFollowUp",
    "liza_liable_party": "DeclarationsOfLiability",
    "liza_peppol": "Peppol",
    "liza_url_payment_experience": "PaymentExperience",
    "liza_country_code": "CountryCode",
}
# Keys to access any data within DATA_KEYS above
NESTED_KEYS = {
    "liza_jur_form": "Abbreviation",
    "liza_companystatus": "Info",
    "liza_companystatus_code": "Code",
    "liza_prefLang_id": "LanguageString",
    "liza_street": "Line1",
    "liza_zip": "PostalCode",
    "liza_city": "City",
    "liza_country_code_address": "CountryCode",
    "liza_balance_year": "FiscalYear",
    "liza_currency_id": "Currency",
    "liza_closed_date": "ToDate",
    "liza_equityCapital": "UNIFIED_Equity",
    "liza_turnover": "UNIFIED_Turnover",
    "liza_average_fte": "UNIFIED_Employees",
    "liza_addedValue": "UNIFIED_ProfitLoss",
    "liza_result": "UNIFIED_GrossMargin",
    # Liza API guidelines: display ScoreAsDecimal (not ScoreAsInt).
    # The barometer image (ScoreImage) still maps to the integer scale.
    "liza_score": "ScoreAsDecimal",
    "liza_image": "ScoreImage",
    "liza_creditLimit": "Limit",
    "liza_creditLimit_info": "Info",
    "liza_warnings": "Warnings",
    "liza_warning_str": "string",
    "liza_industries": "Activity",
    "is_main_industry": "IsMainCategory",
    "industry_name": "Description",
    "industry_code": "Code",
    "balance_data_key": "Key",
    "balance_data_value": "Value",
    "balance_data_dict_main": "Balance",
    "balance_data_dict_parent": "BalanceData",
    "balance_data_dict_child": "BalanceData",
    "liza_liable_party": "LiableParty",
    "liable_party_name": "Name",
    "liable_party_code": "Code",
    "liza_url_payment_experience": "ReportUrl",
}
SEARCH_RESULT_KEYS = {
    "name": "CompanyName",
    "street": "Street",
    "city": "City",
    "country": "Country",
    "country_code": "CountryCode",
    "registry": "RegistrationNumber",
    "is_active": "IsActive",
}
