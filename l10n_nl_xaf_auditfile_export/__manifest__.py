# Copyright 2015 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "XAF auditfile export",
    "version": "11.0.1.3.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "summary": "Export XAF auditfiles for Dutch tax authorities",
    "depends": [
        "base",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/xaf_auditfile_export.xml",
        "views/templates.xml",
        "views/menu.xml",
    ],
    "installable": True,
}
