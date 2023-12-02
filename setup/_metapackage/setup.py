import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-l10n-netherlands",
    description="Meta package for oca-l10n-netherlands Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-l10n_nl_account_tax_unece>=15.0dev,<15.1dev',
        'odoo-addon-l10n_nl_bank>=15.0dev,<15.1dev',
        'odoo-addon-l10n_nl_bsn>=15.0dev,<15.1dev',
        'odoo-addon-l10n_nl_oin>=15.0dev,<15.1dev',
        'odoo-addon-l10n_nl_postcode>=15.0dev,<15.1dev',
        'odoo-addon-l10n_nl_tax_statement>=15.0dev,<15.1dev',
        'odoo-addon-l10n_nl_tax_statement_icp>=15.0dev,<15.1dev',
        'odoo-addon-l10n_nl_xaf_auditfile_export>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
