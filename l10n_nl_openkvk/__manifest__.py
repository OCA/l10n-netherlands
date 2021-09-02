# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Integration with OpenKvK',
    'summary': 'Autocomplete company info using OpenKvK API',
    'version': '12.0.1.0.0',
    'category': 'Localization',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/l10n-netherlands',
    'license': 'AGPL-3',
    'depends': [
        'l10n_nl_kvk',
    ],
    'data': [
        'views/res_config_settings.xml',
    ],
}
