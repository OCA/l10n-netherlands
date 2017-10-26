# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

MAPPING = {
    'btw_0': {'categ': 'tax_categ_z'},
    'btw_6': {'categ': 'tax_categ_aa'},
    'btw_21': {'categ': 'tax_categ_h'},
    'btw_overig': {'categ': 'tax_categ_s'},
    'btw_0_d': {'categ': 'tax_categ_z'},
    'btw_6_d': {'categ': 'tax_categ_aa'},
    'btw_21_d': {'categ': 'tax_categ_h'},
    'btw_overig_d': {'categ': 'tax_categ_s'},
    'btw_6_buy': {'categ': 'tax_categ_aa'},
    'btw_6_buy_incl': {'categ': 'tax_categ_aa'},
    'btw_21_buy': {'categ': 'tax_categ_h'},
    'btw_21_buy_incl': {'categ': 'tax_categ_h'},
    'btw_overig_buy': {'categ': 'tax_categ_s'},
    'btw_6_buy_d': {'categ': 'tax_categ_aa'},
    'btw_21_buy_d': {'categ': 'tax_categ_h'},
    'btw_overig_buy_d': {'categ': 'tax_categ_s'},
    'btw_verk_0': {'categ': 'tax_categ_b'},
    'btw_ink_0_1': {'categ': 'tax_categ_b'},
    'btw_ink_0_2': {'categ': 'tax_categ_b'},
    'btw_ink_0': {'categ': 'tax_categ_b'},
    'btw_I_6_1': {'categ': 'tax_categ_aa'},
    'btw_I_6_2': {'categ': 'tax_categ_aa'},
    'btw_I_6': {'categ': 'tax_categ_aa'},
    'btw_I_21_1': {'categ': 'tax_categ_h'},
    'btw_I_21_2': {'categ': 'tax_categ_h'},
    'btw_I_21': {'categ': 'tax_categ_h'},
    'btw_I_overig_1': {'categ': 'tax_categ_s'},
    'btw_I_overig_2': {'categ': 'tax_categ_s'},
    'btw_I_overig': {'categ': 'tax_categ_s'},
    'btw_X0': {'categ': 'tax_categ_e'},
    'btw_X2': {'categ': 'tax_categ_e'},
    'btw_I_6_d_1': {'categ': 'tax_categ_aa'},
    'btw_I_6_d_2': {'categ': 'tax_categ_aa'},
    'btw_I_6_d': {'categ': 'tax_categ_aa'},
    'btw_I_21_d_1': {'categ': 'tax_categ_h'},
    'btw_I_21_d_2': {'categ': 'tax_categ_h'},
    'btw_I_21_d': {'categ': 'tax_categ_h'},
    'btw_I_overig_d_1': {'categ': 'tax_categ_s'},
    'btw_I_overig_d_2': {'categ': 'tax_categ_s'},
    'btw_I_overig_d': {'categ': 'tax_categ_s'},
    'btw_E1_1': {'categ': 'tax_categ_aa'},
    'btw_E1_2': {'categ': 'tax_categ_aa'},
    'btw_E1': {'categ': 'tax_categ_aa'},
    'btw_E2_1': {'categ': 'tax_categ_h'},
    'btw_E2_2': {'categ': 'tax_categ_h'},
    'btw_E2': {'categ': 'tax_categ_h'},
    'btw_E_overig_1': {'categ': 'tax_categ_s'},
    'btw_E_overig_2': {'categ': 'tax_categ_s'},
    'btw_E_overig': {'categ': 'tax_categ_s'},
    'btw_X1': {'categ': 'tax_categ_b'},
    'btw_X3': {'categ': 'tax_categ_b'},
    'btw_E1_d_1': {'categ': 'tax_categ_aa'},
    'btw_E1_d_2': {'categ': 'tax_categ_aa'},
    'btw_E1_d': {'categ': 'tax_categ_aa'},
    'btw_E2_d_1': {'categ': 'tax_categ_h'},
    'btw_E2_d_2': {'categ': 'tax_categ_h'},
    'btw_E2_d': {'categ': 'tax_categ_h'},
    'btw_E_overig_d_1': {'categ': 'tax_categ_s'},
    'btw_E_overig_d_2': {'categ': 'tax_categ_s'},
    'btw_E_overig_d': {'categ': 'tax_categ_s'},
}


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.multi
    def _l10n_nl_set_unece_on_taxes(self):
        self.ensure_one()
        taxes = self.env['account.tax'].search(
            [('company_id', '=', self.id)])
        ext_id_map = self._l10n_nl_get_external_tax_id_map(taxes)
        for tax in taxes:
            if tax.id in ext_id_map:
                tax_categ = self._l10n_nl_get_tax_categ(ext_id_map, tax)
                external_name = 'account_tax_unece.' + tax_categ
                categ_id = self.env.ref(external_name).id or False
                utype_id = self.env.ref('account_tax_unece.tax_type_vat').id
                tax.write({
                    'unece_type_id': utype_id,
                    'unece_categ_id': categ_id,
                })

    @api.model
    def _l10n_nl_get_tax_categ(self, ext_id_map, tax):
        map_tax_index = str(ext_id_map[tax.id]).split('_', 1)[1]
        mapped_tax_data = MAPPING[map_tax_index]
        return mapped_tax_data['categ']

    @api.model
    def _l10n_nl_get_external_tax_id_map(self, taxes):
        tax_data = self.env['ir.model.data'].search_read([
            ('model', '=', 'account.tax'),
            ('res_id', 'in', taxes.ids)
        ], ['name', 'res_id'])
        map = {}
        for item in tax_data:
            map[item['res_id']] = item['name']
        return map
