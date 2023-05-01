# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Dutch partner names',
    'version': '11.0.0.0.0',
    'author': 'Therp BV, Odoo Community Association (OCA)',
    'category': 'Contact management',
    'website': 'https://github.com/OCA/l10n-netherlands',
    'depends': [
        'partner_firstname',
        'base_view_inheritance_extension',
    ],
    'data': [
        'view/res_partner.xml',
        "data/ir.config_parameter.xml",
    ],
    'auto_install': False,
    'installable': True,
    'external_dependencies': {
        'python': ['mako'],
    },
    'license': 'AGPL-3',
}
