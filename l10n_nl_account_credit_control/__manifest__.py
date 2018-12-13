{
    'name': 'Credit Control for the Netherlands',
    'summary': 'Dutch localization for credit control',
    'license': 'AGPL-3',
    'author': 'Onestein,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/l10n-netherlands',
    'category': 'Localization',
    'version': '11.0.1.0.0',
    'development_status': 'Beta',
    'depends': [
        'account_credit_control',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/credit_control_policy_fee_data.xml',
        'views/credit_control_policy_view.xml',
        'reports/report_credit_control_summary.xml'
    ]
}
