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
    table = "account_move_line"
    for column, datatype in (
            ("l10n_nl_vat_statement_id", "INTEGER"),
            ("l10n_nl_vat_statement_include", "BOOLEAN")):
        if not column_exists(cr, table, column):
            logger.info("Precreating %s.%s", table, column)
            cr.execute(
                "ALTER TABLE {} ADD COLUMN {} {}".format(
                    table, column, datatype))
