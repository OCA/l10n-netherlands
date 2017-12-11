# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Full salutation for partners, Dutch style',
    'version': '10.0.1.1.0',
    'author': 'Therp BV, Odoo Community Association (OCA)',
    'category': 'Contact management',
    'license': 'AGPL-3',
    'website': 'https://github.com/oca/l10n-netherlands.git',
    'depends': [
        'partner_contact_gender',
        'l10n_nl_partner_name',
    ],
    'data': [
        'data/res_partner_title.xml',
        'views/res_partner_title.xml',
        'views/res_partner.xml',
    ],
}
