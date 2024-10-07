import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-l10n-netherlands",
    description="Meta package for oca-l10n-netherlands Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-l10n_nl_account_tax_unece>=16.0dev,<16.1dev',
        'odoo-addon-l10n_nl_bank>=16.0dev,<16.1dev',
        'odoo-addon-l10n_nl_bsn>=16.0dev,<16.1dev',
        'odoo-addon-l10n_nl_oin>=16.0dev,<16.1dev',
        'odoo-addon-l10n_nl_partner_name>=16.0dev,<16.1dev',
        'odoo-addon-l10n_nl_postcode>=16.0dev,<16.1dev',
        'odoo-addon-l10n_nl_tax_statement>=16.0dev,<16.1dev',
        'odoo-addon-l10n_nl_tax_statement_date_range>=16.0dev,<16.1dev',
        'odoo-addon-l10n_nl_tax_statement_icp>=16.0dev,<16.1dev',
        'odoo-addon-l10n_nl_xaf_auditfile_export>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
