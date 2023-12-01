# -*- coding: utf-8 -*-
# Copyright 2015-2023 Therp BV (https://therp.nl).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "XAF auditfile export",
    "version": "9.0.2.0.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-netherlands",
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
