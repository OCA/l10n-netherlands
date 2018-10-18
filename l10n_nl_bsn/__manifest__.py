# Copyright 2016-2018 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Burgerservicenummer (BSN) for Partners',
    'version': '12.0.1.0.0',
    'development_status': 'Production/Stable',
    'category': 'Localization',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'maintainers': ['astirpe'],
    'website': 'https://github.com/OCA/l10n-netherlands',
    'license': 'AGPL-3',
    'depends': [
        'hr',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'external_dependencies': {
        'python': ['stdnum'],
    },
}
