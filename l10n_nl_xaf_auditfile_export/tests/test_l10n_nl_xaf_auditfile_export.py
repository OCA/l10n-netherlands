# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestL10nNlXafAuditfileExport(TransactionCase):
    def test_l10n_nl_xaf_auditfile_export(self):
        export = self.env['xaf.auditfile.export'].create({})
        export.button_generate()
        self.assertTrue(export.auditfile)
