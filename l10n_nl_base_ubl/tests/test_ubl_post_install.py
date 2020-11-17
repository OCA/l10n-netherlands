# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

import odoo
from odoo.tests.common import Form, HttpCase


@odoo.tests.tagged("post_install", "-at_install")
class TestUblInvoice(HttpCase):
    def setUp(self):
        super().setUp()
        with Form(
            self.env["account.move"].with_context(default_type="out_invoice")
        ) as invoice_form:
            invoice_form.partner_id = self.env.ref("base.res_partner_4")
            invoice_form.partner_id.country_id = self.env.ref("base.nl")
            with invoice_form.invoice_line_ids.new() as invoice_line_form:
                invoice_line_form.product_id = self.env.ref("product.product_product_4")
                invoice_line_form.name = "product that cost 100"
                invoice_line_form.quantity = 1
                invoice_line_form.price_unit = 100.0
            self.invoice = invoice_form.save()

    def test_01_ubl_kvk_found(self):
        if self.invoice.partner_id._fields.get("coc_registration_number"):
            self.invoice.partner_id.coc_registration_number = "012345"

            nsmap, ns = self.env["base.ubl"]._ubl_get_nsmap_namespace("Invoice-1")
            xml_root = etree.Element("Invoice", nsmap=nsmap)
            self.env["base.ubl"]._ubl_add_customer_party(
                self.invoice.partner_id, False, "AccountingCustomerParty", xml_root, ns
            )

    def test_02_ubl_oin_found(self):
        if self.invoice.partner_id._fields.get("nl_oin"):
            self.invoice.partner_id.nl_oin = "01234567890123456789"

            nsmap, ns = self.env["base.ubl"]._ubl_get_nsmap_namespace("Invoice-2")
            xml_root = etree.Element("Invoice", nsmap=nsmap)
            self.env["base.ubl"]._ubl_add_customer_party(
                self.invoice.partner_id, False, "AccountingCustomerParty", xml_root, ns
            )
