import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-l10n-netherlands",
    description="Meta package for oca-l10n-netherlands Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-l10n_nl_bsn',
        'odoo9-addon-l10n_nl_intrastat',
        'odoo9-addon-l10n_nl_postcodeapi',
        'odoo9-addon-l10n_nl_tax_statement',
        'odoo9-addon-l10n_nl_xaf_auditfile_export',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 9.0',
    ]
)
