# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree
from mock import patch

from openerp.addons.l10n_nl_base_ubl.tests.test_base import TestBase
from openerp.tests.common import at_install, post_install


@at_install(True)
@post_install(False)
class TestUblInvoice(TestBase):

    def test_01_ubl_emulate_kvk_found(self):
        nsmap, ns = self.env["base.ubl"]._ubl_get_nsmap_namespace("Invoice-1")
        xml_root = etree.Element("Invoice", nsmap=nsmap)

        path_addon = "openerp.addons.l10n_nl_base_ubl."
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

        path_addon = "openerp.addons.l10n_nl_base_ubl."
        path_file = "models.base_ubl."
        classBaseUbl = path_addon + path_file + "BaseUbl."

        with patch(classBaseUbl + "_l10n_nl_base_ubl_get_oin") as _sugg_mock:
            _sugg_mock.return_value = "00000123456789012345"

            self.env["base.ubl"]._ubl_add_customer_party(
                self.invoice.partner_id, False, "AccountingCustomerParty", xml_root, ns
            )
