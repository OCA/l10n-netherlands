# Copyright 2017-2020 Onestein (<https://www.onestein.eu>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase

from ..post_install import set_unece_on_taxes


class TestNlAccountTaxUnece(TransactionCase):
    def setUp(self):
        super().setUp()

        self.my_company = self.env["res.company"].create({"name": "My Dutch Company"})
        l10nnl_chart_template = self.env.ref("l10n_nl.l10nnl_chart_template")
        old_company = self.env.user.company_id
        self.env.user.company_id = self.my_company.id
        l10nnl_chart_template.try_loading()
        self.env.user.company_id = old_company.id

        self.unece_type_id = self.env.ref("account_tax_unece.tax_type_vat").id
        # Allowed NL categories according to NLCIUS
        # Source: forumstandaardisatie.nl/open-standaarden/nlcius
        self.unece_categ_ids = [
            self.env.ref("account_tax_unece.tax_categ_z").id,
            self.env.ref("account_tax_unece.tax_categ_s").id,
            self.env.ref("account_tax_unece.tax_categ_k").id,
            self.env.ref("account_tax_unece.tax_categ_e").id,
            self.env.ref("account_tax_unece.tax_categ_g").id,
            self.env.ref("account_tax_unece.tax_categ_ae").id,
        ]

    def test_load_coa(self):

        unece_type_id = self.unece_type_id
        unece_categ_ids = self.unece_categ_ids

        taxes = self.env["account.tax"].search(
            [("company_id", "=", self.my_company.id)]
        )

        # For each tax account verify that the UNECE values are set
        for tax in taxes:
            self.assertEqual(tax.unece_type_id.id, unece_type_id)
            self.assertIn(tax.unece_categ_id.id, unece_categ_ids)

    def test_existing_coa_update(self):

        taxes = self.env["account.tax"].search(
            [("company_id", "=", self.my_company.id)]
        )

        # For each tax account, force the UNECE values to False
        for tax in taxes:
            tax.unece_type_id = False
            tax.unece_categ_id = False

        # Launch the method that is normally executed by the post_install.py
        self.my_company._l10n_nl_set_unece_on_taxes()

        unece_type_id = self.unece_type_id
        unece_categ_ids = self.unece_categ_ids

        # For each tax account verify that the UNECE values are set
        for tax in taxes:
            self.assertEqual(tax.unece_type_id.id, unece_type_id)
            self.assertIn(tax.unece_categ_id.id, unece_categ_ids)

    def test_post_init_hook(self):

        self.env["res.company"].create({"name": "My New Dutch Company"})
        self.env["res.company"].create(
            {"name": "My New Company", "country_id": self.env.ref("base.it").id}
        )
        set_unece_on_taxes(self.cr, self.env)
