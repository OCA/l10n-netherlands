import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-l10n-netherlands",
    description="Meta package for oca-l10n-netherlands Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-l10n_nl_bank',
        'odoo12-addon-l10n_nl_bsn',
        'odoo12-addon-l10n_nl_postcode',
        'odoo12-addon-l10n_nl_tax_invoice_basis',
        'odoo12-addon-l10n_nl_tax_statement',
        'odoo12-addon-l10n_nl_xaf_auditfile_export',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
