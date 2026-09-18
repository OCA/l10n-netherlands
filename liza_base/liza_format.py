from datetime import datetime

from odoo import tools

from .liza_const import DATA_KEYS, DATE_FORMAT, NESTED_KEYS

# Specific formatting for various liza values


def get_lang_id(env, lang_code):
    lang = (
        env["res.lang"]
        .with_context(active_test=False)
        .search([("iso_code", "=", lang_code)])
    )
    return lang and lang.id or None


def get_country_id(env, country_code):
    country = env["res.country"].search([("code", "=", country_code.upper())])
    return country and country.id or False


def get_currency_id(env, currency_name):
    country = (
        env["res.currency"]
        .with_context(active_test=False)
        .search([("name", "=", currency_name)])
    )
    return country and country.id or False


def format_float_value(value):
    """
    Get float value if present, else set None (required to distinguish 0 from None)
    """
    has_value = value or (value is not False and value == 0)
    return float(value) if has_value else None


def format_date(value):
    try:
        return datetime.strptime(str(value), DATE_FORMAT)
    except ValueError:
        return False


def format_industry(industry_dict):
    return (
        f"{industry_dict[NESTED_KEYS['industry_code']]} - "
        f"{industry_dict[NESTED_KEYS['industry_name']]}"
    )


def format_warnings(warnings):
    return "\n".join(
        f"- {warning}" for warning in warnings.get(NESTED_KEYS["liza_warning_str"])
    )


def format_liable_party(liable_party_dict, env):
    name = liable_party_dict.get(NESTED_KEYS["liable_party_name"], False)
    country_code = liable_party_dict.get(
        NESTED_KEYS["liza_country_code_address"], False
    )
    from_date = tools.format_date(
        env, format_date(liable_party_dict.get(DATA_KEYS["liza_startDate"], False))
    )
    to_date = (
        tools.format_date(env, format_date(end_date))
        if (end_date := liable_party_dict.get(DATA_KEYS["liza_endDate"], False))
        else False
    )
    vat = liable_party_dict.get(DATA_KEYS["liza_vat"], False)
    registry = liable_party_dict.get(DATA_KEYS["liza_registry"], False)
    return (
        f"{name} ({country_code})\n"
        f"{('VAT: ' + vat) if vat else ('Reg: ' + registry)}\n"
        f"Est. {from_date}{(' - ' + to_date) if to_date else ''}"
    )
