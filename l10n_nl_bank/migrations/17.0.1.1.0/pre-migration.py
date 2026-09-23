# Copyright 2025 Emiel van Bokhoven
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Adyen's external id changed from ``ADYEN`` to ``ADYB`` in the regenerated
    # data file (it is now derived from the first four BIC characters, like the
    # other records). Rename the existing external id so the record is updated
    # in place instead of a duplicate being created.
    openupgrade.rename_xmlids(env.cr, [("l10n_nl_bank.ADYEN", "l10n_nl_bank.ADYB")])
