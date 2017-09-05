# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestNlAccountTaxUnece(TransactionCase):

    def test_load_coa(self):
        my_company = self.env['res.company'].create({
            'name': 'My Dutch Company',
            'country_id': self.env.ref('base.nl').id,

        })
        l10nnl_chart_template = self.env.ref('l10n_nl.l10nnl_chart_template')
        transfer_account_id = self.env.ref('l10n_nl.transfer_account_id')
        wizard = self.env['wizard.multi.charts.accounts'].create({
            'company_id': my_company.id,
            'chart_template_id': l10nnl_chart_template.id,
            'transfer_account_id': transfer_account_id.id,
            'code_digits': 6,
            'sale_tax_id': self.env.ref('l10n_nl.btw_21').id,
            'purchase_tax_id': self.env.ref('l10n_nl.btw_21_buy').id,
            'sale_tax_rate': 21.0,
            'purchase_tax_rate': 21.0,
            'complete_tax_set': True,
            'currency_id': my_company.currency_id.id,
            'bank_account_code_prefix': '103',
            'cash_account_code_prefix': '101',
        })
        wizard.execute()

        taxes = self.env['account.tax'].search([
            ('company_id', '=', my_company.id)
        ])
        unece_type_id = self.env.ref('account_tax_unece.tax_type_vat').id
        unece_categ_ids = [
            self.env.ref('account_tax_unece.tax_categ_h').id,
            self.env.ref('account_tax_unece.tax_categ_aa').id,
            self.env.ref('account_tax_unece.tax_categ_z').id,
            self.env.ref('account_tax_unece.tax_categ_s').id,
            self.env.ref('account_tax_unece.tax_categ_b').id,
            self.env.ref('account_tax_unece.tax_categ_e').id
        ]
        for tax in taxes:
            self.assertTrue(tax.unece_type_id.id == unece_type_id)
            self.assertTrue(tax.unece_categ_id.id in unece_categ_ids)
