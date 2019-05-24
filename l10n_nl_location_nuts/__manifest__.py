# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'NUTS Regions for Netherlands',
    'summary': 'NUTS specific options for Netherlands',
    'version': '12.0.1.0.0',
    'category': 'Localisation/Europe',
    'website': 'https://github.com/OCA/l10n-netherlands',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'base_location_nuts',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
}
