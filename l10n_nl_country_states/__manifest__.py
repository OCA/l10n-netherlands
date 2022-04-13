# Copyright 2018-2021 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Dutch country states (Provincies)",
    "version": "12.0.1.1.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-netherlands",
    "license": "AGPL-3",
    "category": "Localization",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/l10n_nl_country_states.xml",
        "data/res_country_state_nl_zip.xml",
    ],
    "installable": True,
}
