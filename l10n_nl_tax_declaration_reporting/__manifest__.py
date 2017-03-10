# -*- coding: utf-8 -*-
# Copyright 2014-2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'VAT Report Netherlands',
    'version': '10.0.1.0.0',
    'category': 'Localization',
    'license': 'AGPL-3',
    'author': 'Onestein, Odoo Community Association (OCA), Odoo SA',
    'website': 'http://www.onestein.eu',
    'depends': [
        'account',
        'report',
        'l10n_nl',
    ],
    'data': [
        'data/report_paperformat.xml',
        'views/account_tax_report.xml',
        'wizard/account_vat_view_nl.xml',
    ],
    'installable': True,
}
