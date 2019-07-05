# -*- encoding: utf-8 -*-
# Copyright 2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.add_fields(env, [
        ('date_start', 'xaf.auditfile.export', 'xaf_auditfile_export',
         'date', False, 'l10n_nl_xaf_auditfile_export'),
        ('date_end', 'xaf.auditfile.export', 'xaf_auditfile_export',
         'date', False, 'l10n_nl_xaf_auditfile_export'),
    ])
    openupgrade.logged_query(
        cr, """
        UPDATE xaf_auditfile_export xae
        SET date_start = ap.date_start
        FROM account_period ap
        WHERE xae.period_start = ap.id
        """
    )
    openupgrade.logged_query(
        cr, """
        UPDATE xaf_auditfile_export xae
        SET date_end = ap.date_stop
        FROM account_period ap
        WHERE xae.period_end = ap.id
        """
    )
