# Copyright 2017-2020 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Full salutation for partners, Dutch style',
    'version': '12.0.1.0.0',
    'author': 'Therp BV, Odoo Community Association (OCA)',
    'category': 'Contact management',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/l10n-netherlands',
    'depends': [
        'partner_contact_gender',
        'l10n_nl_partner_name',
    ],
    'data': [
        'data/res_partner_title.xml',
        'views/res_partner_title.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
}
