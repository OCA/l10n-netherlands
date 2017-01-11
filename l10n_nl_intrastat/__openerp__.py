# -*- coding: utf-8 -*-
# Copyright 2010-2011 Akretion (http://www.akretion.com).
# Modifications Copyright 2012-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Intrastat reporting (ICP) for the Netherlands',
    'version': '8.0.1.0.1',
    'category': 'Localisation/Report Intrastat',
    'license': 'AGPL-3',
    'summary': """Intrastat report for the Netherlands""",
    'author': 'Therp BV, Odoo Community Association (OCA)',
    'website': 'https://launchpad.net/new-report-intrastat',
    'depends': ['intrastat_base'],
    'data': [
        'views/l10n_nl_intrastat.xml',
        'security/ir.model.access.csv',
    ],
}
