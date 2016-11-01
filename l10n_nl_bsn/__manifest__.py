# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Burgerservicenummer (BSN) for Partners',
    'images': [],
    'version': '10.0.0.1.0',
    'category': 'Localization',
    'author': 'ONESTEiN BV,Odoo Community Association (OCA)',
    'website': 'http://www.onestein.eu',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'hr',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'external_dependencies': {
        'python': ['stdnum'],
    },
}
