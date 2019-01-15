import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-l10n-netherlands",
    description="Meta package for oca-l10n-netherlands Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-l10n_nl_account_tax_unece',
        'odoo11-addon-l10n_nl_bank',
        'odoo11-addon-l10n_nl_bsn',
        'odoo11-addon-l10n_nl_cbs_export',
        'odoo11-addon-l10n_nl_country_states',
        'odoo11-addon-l10n_nl_kvk',
        'odoo11-addon-l10n_nl_location_nuts',
        'odoo11-addon-l10n_nl_openkvk',
        'odoo11-addon-l10n_nl_postcode',
        'odoo11-addon-l10n_nl_postcodeapi',
        'odoo11-addon-l10n_nl_tax_invoice_basis',
        'odoo11-addon-l10n_nl_tax_statement',
        'odoo11-addon-l10n_nl_tax_statement_icp',
        'odoo11-addon-l10n_nl_xaf_auditfile_export',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
