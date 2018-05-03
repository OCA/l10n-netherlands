# -*- coding: utf-8 -*-
# Copyright 2015-2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "XAF auditfile export",
    "version": "8.0.2.1.0",
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
        'security/ir.model.access.csv',
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}
