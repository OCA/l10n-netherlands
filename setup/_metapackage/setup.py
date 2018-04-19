import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-l10n-netherlands",
    description="Meta package for oca-l10n-netherlands Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-l10n_nl_account_tax_unece',
        'odoo10-addon-l10n_nl_bank',
        'odoo10-addon-l10n_nl_bsn',
        'odoo10-addon-l10n_nl_cbs_export',
        'odoo10-addon-l10n_nl_country_states',
        'odoo10-addon-l10n_nl_dutch_company_type',
        'odoo10-addon-l10n_nl_intrastat',
        'odoo10-addon-l10n_nl_partner_name',
        'odoo10-addon-l10n_nl_partner_salutation',
        'odoo10-addon-l10n_nl_postcodeapi',
        'odoo10-addon-l10n_nl_tax_invoice_basis',
        'odoo10-addon-l10n_nl_tax_statement',
        'odoo10-addon-l10n_nl_xaf_auditfile_export',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
