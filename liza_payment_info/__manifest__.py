# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Liza Payment Info",
    "summary": "Send your customer payment information to Liza",
    "author": "Dynapps NL,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-netherlands",
    "version": "19.0.1.0.0",
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "data": [
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        "views/res_config_settings.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
    "external_dependencies": {
        "python": [
            "zeep",
        ],
    },
    "depends": ["liza_base", "account"],
}
