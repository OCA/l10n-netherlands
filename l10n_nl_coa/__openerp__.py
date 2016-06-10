# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Netherlands - Accounting (OCA)',
    'version': '9.0.0.1.0',
    'category': 'Localization/Account Charts',
    'author': 'ONESTEiN BV,Odoo Community Association (OCA)',
    'website': 'http://www.onestein.eu',
    'depends': [
        'account',
        'base_vat',
        'base_iban',
    ],
    'data': [
        'data/account_account_tag.xml',
        'data/account_chart_template.xml',
        'data/account.account.template.xml',
        'data/account_tax_template.xml',
        'data/account_fiscal_position_template.xml',
        'data/account_fiscal_position_tax_template.xml',
        'data/account_fiscal_position_account_template.xml',
        'data/account_chart_template.yml',
        'menuitem.xml',
    ],
    'demo': [],
    'auto_install': False,
    'installable': True,
}
