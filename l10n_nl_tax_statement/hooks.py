# Copyright 2020 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo.tools.sql import column_exists


def pre_init_hook(cr):
    """ Precreate these stored related fields that refer to fields that are
    introduced here in the same module in this version (so no value migration
    is required, as all values are empty).
    """
    logger = logging.getLogger(__name__)
    if not column_exists(cr, "account_move_line", "l10n_nl_vat_statement_id"):
        logger.info(
            "Precreating %s.%s",
            "account_move_line",
            "l10n_nl_vat_statement_id"
        )
        cr.execute(
            "ALTER TABLE account_move_line"
            " ADD COLUMN l10n_nl_vat_statement_id INTEGER"
        )
    if not column_exists(cr, "account_move_line", "l10n_nl_vat_statement_include"):
        logger.info(
            "Precreating %s.%s",
            "account_move_line",
            "l10n_nl_vat_statement_include"
        )
        cr.execute(
            "ALTER TABLE account_move_line"
            " ADD COLUMN l10n_nl_vat_statement_include BOOLEAN"
        )
