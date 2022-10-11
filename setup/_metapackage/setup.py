import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-l10n-netherlands",
    description="Meta package for oca-l10n-netherlands Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-l10n_nl_account_invoice_ubl',
        'odoo8-addon-l10n_nl_base_ubl',
        'odoo8-addon-l10n_nl_bsn',
        'odoo8-addon-l10n_nl_chart_rgs',
        'odoo8-addon-l10n_nl_normalize_zip',
        'odoo8-addon-l10n_nl_oin',
        'odoo8-addon-l10n_nl_partner_name',
        'odoo8-addon-l10n_nl_partner_salutation',
        'odoo8-addon-l10n_nl_postcodeapi',
        'odoo8-addon-l10n_nl_tax_declaration_reporting',
        'odoo8-addon-l10n_nl_xaf_auditfile_export',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
