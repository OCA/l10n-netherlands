import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-l10n-netherlands",
    description="Meta package for oca-l10n-netherlands Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-l10n_nl_account_tax_unece',
        'odoo12-addon-l10n_nl_bank',
        'odoo12-addon-l10n_nl_bsn',
        'odoo12-addon-l10n_nl_country_states',
        'odoo12-addon-l10n_nl_dutch_company_type',
        'odoo12-addon-l10n_nl_kvk',
        'odoo12-addon-l10n_nl_location_nuts',
        'odoo12-addon-l10n_nl_mis_reports',
        'odoo12-addon-l10n_nl_openkvk',
        'odoo12-addon-l10n_nl_partner_name',
        'odoo12-addon-l10n_nl_partner_salutation',
        'odoo12-addon-l10n_nl_postcode',
        'odoo12-addon-l10n_nl_postcodeapi',
        'odoo12-addon-l10n_nl_tax_invoice_basis',
        'odoo12-addon-l10n_nl_tax_statement',
        'odoo12-addon-l10n_nl_tax_statement_icp',
        'odoo12-addon-l10n_nl_xaf_auditfile_export',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
