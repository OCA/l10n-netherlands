# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Liza Business Information",
    "summary": (
        "Know exactly who you are doing business with. Enrich Odoo contacts with Liza."
    ),
    "author": "Dynapps NL,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-netherlands",
    "version": "19.0.1.0.0",
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "installable": True,
    "data": [
        "wizards/liza_search_wizard.xml",
        "wizards/liza_search_wizard_line.xml",
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/partner_view.xml",
        "views/res_config_settings.xml",
        "wizards/credential_wizard.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
    "external_dependencies": {
        "python": [
            "zeep",
            "vcrpy-unittest",
        ],
    },
    "depends": ["contacts"],
    "application": True,
}
