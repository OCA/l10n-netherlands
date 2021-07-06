# Copyright 2018 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Netherlands ICP Statement',
    'version': '12.0.1.1.0',
    'category': 'Localization',
    'license': 'AGPL-3',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/l10n-netherlands',
    'depends': [
        'l10n_nl_tax_statement',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'security/ir.model.access.csv',
        'views/l10n_nl_vat_statement_view.xml',
        'views/report_tax_statement.xml',
        'report/report_tax_statement.xml',
    ],
    'installable': True,
}
