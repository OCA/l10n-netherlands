# Copyright 2025 Emiel van Bokhoven
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # The bank data file is flagged ``noupdate="1"``, so the names of records
    # that already exist are not refreshed by a regular upgrade. Reload it in
    # ``init`` mode to apply the updated names (e.g. SNS) and BIC codes to the
    # existing records and to create the newly added banks.
    openupgrade.load_data(env.cr, "l10n_nl_bank", "data/res_bank_data.xml", mode="init")
