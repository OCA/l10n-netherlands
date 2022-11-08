# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Dutch partner names',
    'version': '12.0.1.0.0',
    'author': 'Therp BV, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/l10n-netherlands',
    'category': 'Contact management',
    'depends': [
        'partner_firstname',
    ],
    'data': [
        "views/res_partner.xml",
        "data/ir.config_parameter.xml",
    ],
    'installable': True,
    'license': 'AGPL-3',
}
