# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Let's Encrypt TransIP integration",
    "version": "11.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Administration",
    "summary": "Use TransIP for Let's Encrypt DNS validation",
    "depends": [
        "letsencrypt",
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
    "application": False,
    "external_dependencies": {
        "python": [
            "transip",
        ],
    },
}
