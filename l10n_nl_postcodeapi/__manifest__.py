# Copyright 2013-2021 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Integration with PostcodeApi.nu',
    'summary': 'Autocomplete Dutch addresses using PostcodeApi.nu',
    'version': '11.0.2.0.0',
    'author': 'Therp BV,Odoo Community Association (OCA)',
    'category': 'Localization',
    'website': 'https://github.com/OCA/l10n-netherlands',
    'maintainers': ['NL66278'],  # ronald@therp.nl
    'license': 'AGPL-3',
    'depends': [
        'base_address_extended',
        'l10n_nl_country_states',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        ],
    'external_dependencies': {
        'python': ['pyPostcode'],
    },
    'installable': True,
}
