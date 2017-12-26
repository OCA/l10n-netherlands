# -*- coding: utf-8 -*-
# Copyright 2017-2018 - Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestL10nNlXafAuditfileExport(TransactionCase):

    def test_l10n_nl_xaf_auditfile_export_default(self):
        export = self.env['xaf.auditfile.export'].create({})
        export.button_generate()
        self.assertTrue(export.auditfile)
