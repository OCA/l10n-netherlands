# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    "name": "CBS Export",
    "version": "1.0",
    "author": "Odoo Experts",
    "website": "https://www.odooexperts.nl",
    "category": "Accounting",
    "depends": ["account", "report_intrastat"],
    "summary": "CBS Export File",
    "description": """
        CBS Export File
    """,
    "data": [
        "security/ir.model.access.csv",
        "view/cbs_export_file_sequence.xml",
        "data/cron_process_cbs_export.xml",
        "view/cbs_export_file_view.xml",
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
