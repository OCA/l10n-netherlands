# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Netherlands ICP Statement (apart from BTW)",
    "summary": "Manage your BTW and ICP statements separately",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Localization",
    "website": "https://github.com/OCA/l10n-netherlands",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "depends": [
        "l10n_nl_tax_statement_icp",
    ],
    "data": [
        "data/ir_actions_report.xml",
        "security/ir.model.access.csv",
        "views/l10n_nl_icp_statement.xml",
        "views/l10n_nl_vat_statement.xml",
    ],
}
