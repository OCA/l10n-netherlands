import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-l10n-netherlands",
    description="Meta package for oca-l10n-netherlands Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-l10n_nl_account_tax_unece',
        'odoo13-addon-l10n_nl_bank',
        'odoo13-addon-l10n_nl_bsn',
        'odoo13-addon-l10n_nl_location_nuts',
        'odoo13-addon-l10n_nl_mis_reports',
        'odoo13-addon-l10n_nl_oin',
        'odoo13-addon-l10n_nl_postcode',
        'odoo13-addon-l10n_nl_tax_invoice_basis',
        'odoo13-addon-l10n_nl_tax_statement',
        'odoo13-addon-l10n_nl_tax_statement_icp',
        'odoo13-addon-l10n_nl_xaf_auditfile_export',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
