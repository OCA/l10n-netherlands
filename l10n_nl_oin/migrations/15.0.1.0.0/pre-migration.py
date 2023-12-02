# Copyright 2023 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """In the Dutch localization of Odoo 15.0 a new field 'l10n_nl_oin' was added.
    This method renames old field 'nl_oin' to 'l10n_nl_oin', in order to preserve
    existing values.
    """
    openupgrade.rename_fields(
        env,
        [
            (
                "res.partner",
                "res_partner",
                "nl_oin",
                "l10n_nl_oin",
            )
        ],
    )
