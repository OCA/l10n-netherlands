# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# Copyright 2018 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestL10nNlXafAuditfileExport(TransactionCase):

    def setUp(self):
        super(TestL10nNlXafAuditfileExport, self).setUp()
        self.fiscalyear = self.env['account.fiscalyear'].browse(
            self.env['account.fiscalyear'].find()
        )
        self.export = self.env['xaf.auditfile.export'].create({})
        # depending on other modules installed, we get some undefined
        # fiscal year via defaults, force this to the current year
        # in order to be sure we get account's demo data
        self.export.write({
            'period_start': self.fiscalyear.period_ids[0].id,
            'period_end': self.fiscalyear.period_ids[-1].id,
        })

    def test_l10n_nl_xaf_auditfile_export_default(self):
        self.export.button_generate()
        self.assertTrue(self.export.auditfile)

    def test_l10n_nl_xaf_auditfile_export_all(self):
        self.export.write({'data_export': 'all'})
        self.export.button_generate()
        self.assertTrue(self.export.auditfile)
