# Copyright 2015 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "XAF auditfile export",
    "version": "13.0.1.0.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-netherlands",
    "license": "AGPL-3",
    "category": "Invoices & Payments",
    "summary": "Export XAF auditfiles for Dutch tax authorities",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/xaf_auditfile_export.xml",
        "views/templates.xml",
        "views/menu.xml",
    ],
    "installable": True,
}
