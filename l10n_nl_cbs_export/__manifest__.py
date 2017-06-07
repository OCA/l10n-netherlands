# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    "name": "CBS Export Intrahandel Sale",
    "version": "1.0",
    "author": "Odoo Experts",
    "website": "https://www.odooexperts.nl",
    "category": "Accounting",
    "depends": ["account", "report_intrastat"],
    "summary": "CBS Export File for Dutch Intrahandel Sale",
    "description": """
        CBS Export File for Dutch Intrahandel Sale
        
        See also: https://www.cbs.nl/nl-nl/deelnemers-enquetes/deelnemers-enquetes/bedrijven/onderzoek/lopend/internationale-handel-in-goederen/idep-codelijsten
        
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
