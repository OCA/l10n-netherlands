# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree
from mock import patch

from odoo.tests.common import Form, HttpCase


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

    def test_01_ubl_emulate_kvk_found(self):
        nsmap, ns = self.env["base.ubl"]._ubl_get_nsmap_namespace("Invoice-1")
        xml_root = etree.Element("Invoice", nsmap=nsmap)

        path_addon = "odoo.addons.l10n_nl_base_ubl."
        path_file = "models.base_ubl."
        classBaseUbl = path_addon + path_file + "BaseUbl."

        with patch(classBaseUbl + "_l10n_nl_base_ubl_get_kvk") as _sugg_mock:
            _sugg_mock.return_value = "12345"

            self.env["base.ubl"]._ubl_add_customer_party(
                self.invoice.partner_id, False, "AccountingCustomerParty", xml_root, ns
            )

    def test_02_ubl_emulate_oin_found(self):
        nsmap, ns = self.env["base.ubl"]._ubl_get_nsmap_namespace("Invoice-2")
        xml_root = etree.Element("Invoice", nsmap=nsmap)

        path_addon = "odoo.addons.l10n_nl_base_ubl."
        path_file = "models.base_ubl."
        classBaseUbl = path_addon + path_file + "BaseUbl."

        with patch(classBaseUbl + "_l10n_nl_base_ubl_get_oin") as _sugg_mock:
            _sugg_mock.return_value = "00000123456789012345"

            self.env["base.ubl"]._ubl_add_customer_party(
                self.invoice.partner_id, False, "AccountingCustomerParty", xml_root, ns
            )
