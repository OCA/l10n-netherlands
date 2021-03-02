import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-l10n-netherlands",
    description="Meta package for oca-l10n-netherlands Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-l10n_nl_account_tax_unece',
        'odoo14-addon-l10n_nl_bsn',
        'odoo14-addon-l10n_nl_oin',
        'odoo14-addon-l10n_nl_postcode',
        'odoo14-addon-l10n_nl_tax_statement',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
