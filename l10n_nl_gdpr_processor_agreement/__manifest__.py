# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Data processor agreement",
    "version": "10.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Data Protection",
    "summary": "Print data processor agreements for your customers",
    "depends": [
        'report_py3o',
    ],
    "demo": [
        "demo/res_partner.xml",
    ],
    "data": [
        "data/res_partner_category.xml",
        "data/ir_actions_report_xml.xml",
    ],
    "installable": True,
}
