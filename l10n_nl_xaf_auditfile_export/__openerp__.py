# -*- coding: utf-8 -*-
# Copyright (C) 2015 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "XAF auditfile export",
    "version": "8.0.2.0.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "summary": "Export XAF auditfiles for Dutch tax authorities",
    "depends": [
        'base',
        'account',
    ],
    "data": [
        "demo/res_partner.xml",
        "views/xaf_auditfile_export.xml",
        "views/menu.xml",
        'views/xaf_template_all.xml',
        'views/xaf_template_default.xml',
        'security/ir.model.access.csv',
    ],
    "qweb": [
    ],
    "test": [
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies": {
        'python': [],
    },
}
