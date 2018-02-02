# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase, at_install, post_install


@at_install(False)
@post_install(True)
class TestNlAccountTaxUnece(TransactionCase):

    def setUp(self):
        super(TestNlAccountTaxUnece, self).setUp()

        self.my_company = self.env['res.company'].create({
            'name': 'My Dutch Company',
            'country_id': self.env.ref('base.nl').id,
        })
        l10nnl_chart_template = self.env.ref('l10n_nl.l10nnl_chart_template')
        transfer_account_id = self.env.ref('l10n_nl.transfer_account_id')
        self.wizard = self.env['wizard.multi.charts.accounts'].create({
            'company_id': self.my_company.id,
            'chart_template_id': l10nnl_chart_template.id,
            'transfer_account_id': transfer_account_id.id,
            'code_digits': 6,
            'sale_tax_id': self.env.ref('l10n_nl.btw_21').id,
            'purchase_tax_id': self.env.ref('l10n_nl.btw_21_buy').id,
            'sale_tax_rate': 21.0,
            'purchase_tax_rate': 21.0,
            'complete_tax_set': True,
            'currency_id': self.my_company.currency_id.id,
            'bank_account_code_prefix': '103',
            'cash_account_code_prefix': '101',
        })

        self.unece_type_id = self.env.ref('account_tax_unece.tax_type_vat').id
        self.unece_categ_ids = [
            self.env.ref('account_tax_unece.tax_categ_h').id,
            self.env.ref('account_tax_unece.tax_categ_aa').id,
            self.env.ref('account_tax_unece.tax_categ_z').id,
            self.env.ref('account_tax_unece.tax_categ_s').id,
            self.env.ref('account_tax_unece.tax_categ_b').id,
            self.env.ref('account_tax_unece.tax_categ_e').id
        ]

    def test_load_coa(self):

        # Set the Dutch chart of accounts for the company
        self.wizard.execute()

        unece_type_id = self.unece_type_id
        unece_categ_ids = self.unece_categ_ids

        taxes = self.env['account.tax'].search([
            ('company_id', '=', self.my_company.id)
        ])

        # For each tax account verify that the UNECE values are set
        for tax in taxes:
            self.assertTrue(tax.unece_type_id.id == unece_type_id)
            self.assertTrue(tax.unece_categ_id.id in unece_categ_ids)

    def test_existing_coa_update(self):

        # Set the Dutch chart of accounts for the company
        self.wizard.execute()

        taxes = self.env['account.tax'].search([
            ('company_id', '=', self.my_company.id)
        ])

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
            self.assertTrue(tax.unece_type_id.id == unece_type_id)
            self.assertTrue(tax.unece_categ_id.id in unece_categ_ids)
