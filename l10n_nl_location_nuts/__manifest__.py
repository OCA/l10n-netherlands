# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'NUTS Regions for Netherlands',
    'summary': 'NUTS specific options for Netherlands',
    'version': '11.0.1.0.0',
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
