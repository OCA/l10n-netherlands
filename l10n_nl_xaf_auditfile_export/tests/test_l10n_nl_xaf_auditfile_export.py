# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import os
from datetime import timedelta
from io import BytesIO
from zipfile import ZipFile

from lxml import etree

from odoo import fields
from odoo.tests.common import Form, tagged
from odoo.tools import mute_logger

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


def xaf_xpath(auditfile, query):
    with ZipFile(BytesIO(base64.b64decode(auditfile)), "r") as z:
        contents = z.read(z.filelist[-1]).decode()
        parser = etree.XMLParser(
            ns_clean=True, recover=True, encoding="utf-8", remove_blank_text=True
        )
        root = etree.XML(bytes(contents, encoding="utf8"), parser=parser)
        yield from root.xpath(
            query, namespaces={"a": "http://www.auditfiles.nl/XAF/3.2"}
        )


def get_transaction_line_count_from_xml(auditfile):
    """Helper XML method to parse and return the transaction line count"""
    line_count = 0
    # xpath query to select all element nodes in namespace
    # Source: https://stackoverflow.com/a/30233635
    query = "descendant-or-self::*[namespace-uri()!='']"
    root = None
    for element in xaf_xpath(auditfile, query):
        element.tag = etree.QName(element).localname
        root = root or element.getroottree()
    if not root:
        return 0
    journals = root.xpath("/auditfile/company/transactions/journal")
    for journal in journals:
        transactions = journal.xpath("transaction/trLine")
        for _ in transactions:
            line_count += 1
    return line_count


@tagged("post_install_l10n", "post_install", "-at_install")
class TestXafAuditfileExport(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref="nl"):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.env.user.company_id = cls.company_data["company"]

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
        self.assertTrue(record.auditfile_success)

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
        self.assertFalse(record.auditfile_success)
        # still contains the faulty auditfile for debugging purposes
        self.assertTrue(record.auditfile)
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
        self.assertTrue(parsed_line_count == line_count)

        # archive all journals
        all_journals = record.get_journals()
        all_journals.write({"active": False})
        self.assertTrue(all(not j.active for j in all_journals))

        record_after = self.env["xaf.auditfile.export"].create({})
        record_after.button_generate()
        self.assertTrue(record_after)

        line_count_after = record_after.get_move_line_count()
        parsed_count_after = get_transaction_line_count_from_xml(record_after.auditfile)
        self.assertTrue(parsed_line_count == parsed_count_after == line_count_after)

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

    @mute_logger("odoo.addons.l10n_nl_xaf_auditfile_export.models.xaf_auditfile_export")
    def test_08_invalid_characters(self):
        """Error because of invalid characters in an auditfile"""
        record = (
            self.env["xaf.auditfile.export"]
            .with_context(dont_sanitize_xml=True)
            .create({})
        )
        # add an invalid character
        record.company_id.name += chr(0x0B)
        record.button_generate()

        self.assertTrue(record)
        self.assertTrue(record.name)
        self.assertFalse(record.auditfile_success)

    def test_09_opening_balance(self):
        """Test that we calculate the opening balance correctly"""
        record = self.env["xaf.auditfile.export"].create({})

        acc_receivable = self.env["account.account"].search(
            [
                (
                    "account_type",
                    "=",
                    "asset_receivable",
                ),
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
        acc_payable = self.env["account.account"].search(
            [
                ("account_type", "=", "liability_payable"),
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
        acc_revenue = self.env["account.account"].search(
            [
                ("account_type", "=", "income"),
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
        journal = self.env["account.journal"].search(
            [
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )

        move_receivable = self.env["account.move"].create(
            {
                "journal_id": journal.id,
                "date": record.date_start - timedelta(days=1),
                "line_ids": [
                    (0, 0, {"account_id": acc_receivable.id, "credit": 42, "debit": 0}),
                    (0, 0, {"account_id": acc_revenue.id, "credit": 0, "debit": 42}),
                ],
            }
        )
        move_payable = self.env["account.move"].create(
            {
                "journal_id": journal.id,
                "date": record.date_start - timedelta(days=1),
                "line_ids": [
                    (0, 0, {"account_id": acc_payable.id, "credit": 0, "debit": 4242}),
                    (0, 0, {"account_id": acc_revenue.id, "credit": 4242, "debit": 0}),
                ],
            }
        )

        move_receivable.action_post()
        self.env.flush_all()
        record.button_generate()

        def xaf_val(auditfile, xpath):
            return float("".join(xaf_xpath(auditfile, xpath)))

        total_credit = xaf_val(
            record.auditfile, "//a:openingBalance/a:totalCredit/text()"
        )
        self.assertEqual(total_credit, 42)
        total_debit = xaf_val(
            record.auditfile, "//a:openingBalance/a:totalDebit/text()"
        )
        self.assertEqual(total_debit, 0)
        lines_count = xaf_val(
            record.auditfile, "//a:openingBalance/a:linesCount/text()"
        )
        self.assertEqual(lines_count, 1)

        move_payable.action_post()
        record = self.env["xaf.auditfile.export"].create({})
        self.env.flush_all()
        record.button_generate()
        total_credit = xaf_val(
            record.auditfile, "//a:openingBalance/a:totalCredit/text()"
        )
        self.assertEqual(total_credit, 42)
        total_debit = xaf_val(
            record.auditfile, "//a:openingBalance/a:totalDebit/text()"
        )
        self.assertEqual(total_debit, 4242)
        lines_count = xaf_val(
            record.auditfile, "//a:openingBalance/a:linesCount/text()"
        )
        self.assertEqual(lines_count, 2)
