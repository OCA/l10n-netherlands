# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from openerp.addons.l10n_nl_base_ubl.tests.test_base import TestBase
from openerp.tests.common import at_install, post_install


@at_install(False)
@post_install(True)
class TestUblInvoice(TestBase):

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
