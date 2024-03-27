# 2021 Bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

"""
The unece tags have been set with the no update tag.
Use openupgradelib to force load the changes.
"""


import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)
try:
    from openupgradelib import openupgrade
except ImportError:
    openupgrade = None


def set_unece_on_taxes(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for company in env["res.company"].search([]):
            company._l10n_nl_set_unece_on_taxes()


def migrate(cr, version):
    if openupgrade is None:
        _logger.warning(
            "OpenUpgradeLib is not found, can't update l10n_nl_account_tax_unece tags"
        )
        return
    _logger.warning("OpenUpgradeLib is going to upgrade nl l10n_nl_account_tax_unece")
    openupgrade.load_data(
        cr, "l10n_nl_account_tax_unece", "data/account_tax_template.xml", mode="init"
    )
    set_unece_on_taxes(cr)
