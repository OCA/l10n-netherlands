# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import os
from io import BytesIO
from zipfile import ZipFile

from lxml import etree

from odoo import fields
from odoo.tests.common import Form, TransactionCase
from odoo.tools import mute_logger


def get_transaction_line_count_from_xml(auditfile):
    """Helper XML method to parse and return the transaction line count"""
    line_count = 0
    with ZipFile(BytesIO(base64.b64decode(auditfile)), "r") as z:
        contents = z.read(z.filelist[-1]).decode()
        parser = etree.XMLParser(
            ns_clean=True, recover=True, encoding="utf-8", remove_blank_text=True
        )
        root = etree.XML(bytes(contents, encoding="utf8"), parser=parser)
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
    """Test export of XAF Auditfile."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.eur = cls.env["res.currency"].search([("name", "=", "EUR")])
        cls.coa = cls.env.ref("l10n_nl.l10nnl_chart_template", raise_if_not_found=False)
        cls.coa = cls.coa or cls.env.ref("l10n_generic_coa.configurable_chart_template")
        cls.company_nl = cls.env["res.company"].create(
            {
                "name": "XAF Company1",
                "country_id": cls.env.ref("base.nl").id,
                "currency_id": cls.eur.id,
            }
        )
        cls.env.user.company_id = cls.company_nl
        cls.coa.try_loading(cls.company_nl, install_demo=False)

        # create an invoice and post it, to ensure that there's some data to export
        move_form = Form(
            cls.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.invoice_date = fields.Date().today()
        move_form.partner_id = cls.env["res.partner"].create({"name": "Partner Test"})
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = cls.env["product.product"].create(
                {"name": "product test", "standard_price": 800.0}
            )
        cls.invoice = move_form.save()
        cls.invoice.action_post()

    def test_01_default_values(self):
        """Check that the default values are filled on creation"""
        record = self.env["xaf.auditfile.export"].create({})

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
        """Do a basic auditfile export"""
        record = self.env["xaf.auditfile.export"].create({})
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
        with ZipFile(zf, "r") as archive:
            filelist = archive.filelist
            contents = archive.read(filelist[-1]).decode()
        self.assertTrue(contents.startswith("<?xml "))

    @mute_logger("odoo.addons.l10n_nl_xaf_auditfile_export.models.xaf_auditfile_export")
    def test_03_export_error(self):
        """Failure to export an auditfile"""
        record = self.env["xaf.auditfile.export"].create({})
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
        """Do a basic auditfile export (no Unit4)"""
        record = self.env["xaf.auditfile.export"].create({})
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

        if record.auditfile_name[-4:] == ".zip":
            zf = BytesIO(base64.b64decode(record.auditfile))
            with ZipFile(zf, "r") as archive:
                filelist = archive.filelist
                contents = archive.read(filelist[-1]).decode()
            self.assertTrue(contents.startswith("<?xml "))

    def test_05_export_success(self):
        """Export auditfile with / character in filename"""
        record = self.env["xaf.auditfile.export"].create({})
        record.name += "%s01" % os.sep
        record.button_generate()
        self.assertTrue(record)

    def test_06_include_moves_from_inactive_journals(self):
        """Include moves off of inactive journals"""
        record = self.env["xaf.auditfile.export"].create({})
        record.button_generate()
        self.assertTrue(record)

        line_count = record.get_move_line_count()
        parsed_line_count = get_transaction_line_count_from_xml(record.auditfile)
        self.assertEqual(parsed_line_count, line_count)

        # archive all journals
        all_journals = record.get_journals()
        all_journals.write({"active": False})
        self.assertTrue(all(not j.active for j in all_journals))

        record_after = self.env["xaf.auditfile.export"].create({})
        record_after.button_generate()
        self.assertTrue(record_after)

        line_count_after = record_after.get_move_line_count()
        parsed_count_after = get_transaction_line_count_from_xml(record_after.auditfile)
        self.assertEqual(parsed_line_count, parsed_count_after)
        self.assertEqual(parsed_count_after, line_count_after)

    def test_07_do_not_include_section_and_note_move_lines(self):
        """Do not include Section and Note move lines"""
        self.env["account.move.line"].create(
            [
                {
                    "name": "Section test",
                    "display_type": "line_section",
                    "move_id": self.invoice.id,
                },
                {
                    "name": "Note test",
                    "display_type": "line_note",
                    "move_id": self.invoice.id,
                },
            ]
        )
        record = self.env["xaf.auditfile.export"].create({})
        record.button_generate()
        self.assertTrue(record)

        line_count = record.get_move_line_count()
        parsed_line_count = get_transaction_line_count_from_xml(record.auditfile)
        self.assertEqual(parsed_line_count, line_count)
