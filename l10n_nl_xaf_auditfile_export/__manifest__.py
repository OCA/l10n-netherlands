# Copyright 2015 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "XAF auditfile export",
    "version": "14.0.3.1.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-netherlands",
    "license": "AGPL-3",
    "category": "Localization/Netherlands",
    "summary": "Export XAF auditfiles for Dutch tax authorities",
    "depends": ["account"],
    "data": [
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/xaf_auditfile_export.xml",
        "views/templates.xml",
        "views/menu.xml",
    ],
    "installable": True,
}
