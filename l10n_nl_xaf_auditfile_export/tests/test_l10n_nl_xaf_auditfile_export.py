# Copyright 2018 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from lxml import etree
from io import BytesIO
import os
from zipfile import ZipFile

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


def get_transaction_line_count_from_xml(auditfile):
    ''' Helper XML method to parse and return the transaction line count '''
    line_count = 0
    with ZipFile(BytesIO(base64.b64decode(auditfile)), 'r') as z:
        contents = z.read(z.filelist[-1]).decode()
        parser = etree.XMLParser(
            ns_clean=True,
            recover=True,
            encoding="utf-8",
            remove_blank_text=True
        )
        root = etree.XML(bytes(contents, encoding='utf8'), parser=parser)
        # xpath query to select all element nodes in namespace
        # Source: https://stackoverflow.com/a/30233635
        query = "descendant-or-self::*[namespace-uri()!='']"
        for element in root.xpath(query):
            element.tag = etree.QName(element).localname
        journals = root.xpath("/auditfile/company/transactions/journal")
        for journal in journals:
            transactions = journal.xpath("transaction/trLine")
            for _ in transactions:
                line_count += 1
    return line_count


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

    def test_05_export_success(self):
        ''' Export auditfile with / character in filename '''
        record = self.env['xaf.auditfile.export'].create({})
        record.name += '%s01' % os.sep
        record.button_generate()
        self.assertTrue(record)

    def test_06_include_moves_from_inactive_journals(self):
        ''' Include moves off of inactive journals '''
        record = self.env['xaf.auditfile.export'].create({})
        record.button_generate()
        self.assertTrue(record)

        line_count = record.get_move_line_count()
        parsed_line_count = get_transaction_line_count_from_xml(record.auditfile)
        self.assertTrue(parsed_line_count == line_count)

        # archive all journals
        all_journals = record.get_journals()
        all_journals.write({'active': False})
        self.assertTrue(all(not j.active for j in all_journals))

        record_after = self.env['xaf.auditfile.export'].create({})
        record_after.button_generate()
        self.assertTrue(record_after)

        line_count_after = record_after.get_move_line_count()
        parsed_count_after = get_transaction_line_count_from_xml(record_after.auditfile)
        self.assertTrue(parsed_line_count == parsed_count_after == line_count_after)
