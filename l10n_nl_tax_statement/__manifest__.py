# Copyright 2017 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Netherlands BTW Statement',
    'version': '11.0.2.1.0',
    'category': 'Localization',
    'license': 'AGPL-3',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/l10n-netherlands',
    'depends': [
        'account_tax_balance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/tax_statement_security_rule.xml',
        'data/paperformat.xml',
        'templates/assets.xml',
        'views/l10n_nl_vat_statement_view.xml',
        'views/report_tax_statement.xml',
        'report/report_tax_statement.xml',
        'wizard/l10n_nl_vat_statement_config_wizard.xml',
    ],
    'installable': True,
}
