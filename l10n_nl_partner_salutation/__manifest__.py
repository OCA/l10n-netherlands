# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Full salutation for partners, Dutch style',
    'version': '10.0.1.0.0',
    'author': 'Therp BV, Odoo Community Association (OCA)',
    'category': 'Contact management',
    "license": "AGPL-3",
    'depends': [
        'l10n_nl_partner_name',
    ],
    'data': [
        'data/res_partner_title.xml',
        'view/res_partner_title.xml',
        'view/res_partner.xml',
        ],
}
