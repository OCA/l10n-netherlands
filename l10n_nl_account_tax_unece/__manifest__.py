# Copyright 2017-2023 Onestein (<https://www.onestein.eu>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "L10n NL Account Tax UNECE",
    "summary": "Auto-configure UNECE params on Dutch taxes",
    "version": "16.0.1.0.0",
    "category": "Localization",
    "author": "Onestein, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-netherlands",
    "license": "LGPL-3",
    "depends": ["l10n_nl", "account_tax_unece"],
    "data": ["data/account_tax_template.xml"],
    "post_init_hook": "set_unece_on_taxes",
    "installable": True,
    "auto_install": True,
}
