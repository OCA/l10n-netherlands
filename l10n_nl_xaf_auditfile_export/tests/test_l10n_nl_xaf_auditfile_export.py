# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import os
from io import BytesIO
from zipfile import ZipFile

from odoo import fields
from odoo.tests.common import Form, TransactionCase
from odoo.tools import mute_logger


class TestXafAuditfileExport(TransactionCase):
    def setUp(self):
        super().setUp()

        self.env.user.company_id.country_id = (self.env.ref("base.nl").id,)

        # create an invoice and post it, to ensure that there's some data to export
        move_form = Form(
            self.env["account.move"].with_context(default_type="out_invoice")
        )
        move_form.invoice_date = fields.Date().today()
        move_form.partner_id = self.env["res.partner"].create({"name": "Partner Test"})
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.env["product.product"].create(
                {"name": "product test", "standard_price": 800.0}
            )
        self.invoice = move_form.save()
        self.invoice.post()

    def test_01_default_values(self):
        """ Check that the default values are filled on creation """
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
        """ Do a basic auditfile export """
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
        """ Failure to export an auditfile """
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
        """ Do a basic auditfile export (no Unit4) """
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
        """ Export auditfile with / character in filename """
        record = self.env["xaf.auditfile.export"].create({})
        record.name += "%s01" % os.sep
        record.button_generate()
        self.assertTrue(record)
