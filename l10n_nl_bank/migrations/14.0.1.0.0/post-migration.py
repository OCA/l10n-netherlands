# 2021 Bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

"""
The banks have been created with the no update tag.
Use openupgradelib to force load the changes.
Old entries will be unchanged,
new entries will be added and existing entries will be updated.
"""


import logging

_logger = logging.getLogger(__name__)
try:
    from openupgradelib import openupgrade
except ImportError:
    openupgrade = None


def migrate(cr, version):
    if openupgrade is None:
        _logger.warning("OpenUpgradeLib is not found, can't update dutch bank data")
        return

    openupgrade.load_data(cr, "l10n_nl_bank", "data/res_bank_data.xml", mode="init")
