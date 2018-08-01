# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from io import BytesIO
from zipfile import ZipFile

from odoo.tools import mute_logger
from odoo.tests.common import TransactionCase


class TestXafAuditfileExport(TransactionCase):

    def test_01_default_values(self):
        ''' Check that the default values are filled on creation '''
        record = self.env['xaf.auditfile.export'].create({})

        self.assertTrue(record)
        self.assertTrue(record.name)
        self.assertFalse(record.auditfile)
        self.assertTrue(record.auditfile_name)
        self.assertTrue(record.company_id)
        self.assertTrue(record.date_start)
        self.assertTrue(record.date_end)
        self.assertFalse(record.date_generated)
        self.assertTrue(record.fiscalyear_name)
        self.assertFalse(record.unit4)

    def test_02_export_success(self):
        ''' Do a basic auditfile export '''
        record = self.env['xaf.auditfile.export'].create({})
        record.button_generate()

        self.assertTrue(record.name)
        self.assertTrue(record.auditfile)
        self.assertTrue(record.auditfile_name)
        self.assertTrue(record.company_id)
        self.assertTrue(record.date_start)
        self.assertTrue(record.date_end)
        self.assertTrue(record.date_generated)
        self.assertTrue(record.fiscalyear_name)
        self.assertFalse(record.unit4)

        zf = BytesIO(base64.b64decode(record.auditfile))
        with ZipFile(zf, 'r') as archive:
            filelist = archive.filelist
            contents = archive.read(filelist[-1]).decode()
        self.assertTrue(contents.startswith('<?xml '))

    @mute_logger(
        'odoo.addons.l10n_nl_xaf_auditfile_export.models.xaf_auditfile_export'
    )
    def test_03_export_error(self):
        ''' Failure to export an auditfile '''
        record = self.env['xaf.auditfile.export'].create({})
        record.company_id.country_id = False
        record.button_generate()

        self.assertTrue(record)
        self.assertTrue(record.name)
        self.assertFalse(record.auditfile)
        self.assertTrue(record.auditfile_name)
        self.assertTrue(record.company_id)
        self.assertTrue(record.date_start)
        self.assertTrue(record.date_end)
        self.assertTrue(record.date_generated)
        self.assertTrue(record.fiscalyear_name)
        self.assertFalse(record.unit4)

    def test_04_export_success_unit4(self):
        ''' Do a basic auditfile export (no Unit4) '''
        record = self.env['xaf.auditfile.export'].create({})
        record.unit4 = True
        record.button_generate()

        self.assertTrue(record.name)
        self.assertTrue(record.auditfile)
        self.assertTrue(record.auditfile_name)
        self.assertTrue(record.company_id)
        self.assertTrue(record.date_start)
        self.assertTrue(record.date_end)
        self.assertTrue(record.date_generated)
        self.assertTrue(record.fiscalyear_name)
        self.assertTrue(record.unit4)

        if record.auditfile_name[-4:] == '.zip':
            zf = BytesIO(base64.b64decode(record.auditfile))
            with ZipFile(zf, 'r') as archive:
                filelist = archive.filelist
                contents = archive.read(filelist[-1]).decode()
            self.assertTrue(contents.startswith('<?xml '))
