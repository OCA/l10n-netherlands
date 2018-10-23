# Copyright 2017-2018 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'NL Tax Invoice Basis (Factuurstelsel)',
    'summary': 'Enable invoice basis on tax according to the Dutch law',
    'version': '12.0.1.0.0',
    'development_status': 'Production/Stable',
    'category': 'Localization',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'maintainers': ['astirpe'],
    'website': 'https://github.com/OCA/l10n-netherlands',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'account_tax_balance',
    ],
    'data': [
        'views/res_config_settings.xml',
    ],
    'installable': True,
}
