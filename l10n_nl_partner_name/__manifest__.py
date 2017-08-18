# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Dutch partner names',
    'version': '10.0.1.0.0',
    'author': 'Therp BV, Odoo Community Association (OCA)',
    'category': 'Contact management',
    'depends': [
        'partner_firstname',
    ],
    'data': [
        'view/res_partner.xml',
    ],
    'auto_install': False,
    'installable': True,
    'external_dependencies': {
        'python': ['mako'],
    },
}
