# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Integration with Kamer van Koophandel',
    'summary': 'Autocomplete company info using KvK API Search',
    'version': '11.0.1.0.0',
    'category': 'Localization',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/l10n-netherlands',
    'license': 'AGPL-3',
    'depends': [
        'partner_coc',
        'base_setup',
    ],
    'data': [
        'views/res_config_settings.xml',
        'views/res_partner.xml',
        'wizards/l10n_nl_kvk_preview_wizard.xml',
    ],
}
