# Copyright 2023 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Netherlands BTW Statement - Date range",
    "version": "16.0.1.0.0",
    "category": "Localization",
    "license": "AGPL-3",
    "author": "Onestein, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-netherlands",
    "depends": ["l10n_nl_tax_statement", "date_range"],
    "data": [
        "views/l10n_nl_vat_statement_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
