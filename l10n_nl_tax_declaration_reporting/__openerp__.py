# -*- coding: utf-8 -*-
# © 2014-2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'VAT Report Netherlands',
    'images': [],
    'version': '8.0.1.0.0',
    'category': 'Localization',
    'license': 'AGPL-3',
    'author': 'ONESTEiN BV, Odoo Community Association (OCA), Odoo SA',
    'website': 'http://www.onestein.nl',
    'depends': [
        'account',
        'account_chart',
    ],
    'data': [
        'views/account_tax_report.xml',
        'wizard/account_vat_view_nl.xml',
    ],
}
