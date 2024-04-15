# Copyright 2017-2020 Onestein (<https://www.onestein.eu>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _l10n_nl_set_unece_on_taxes(self):
        self.ensure_one()
        taxes = self.env["account.tax"].search([("company_id", "=", self.id)])
        ext_id_map = self._l10n_nl_get_external_tax_id_map(taxes)
        utype_id = self.env.ref("account_tax_unece.tax_type_vat").id
        for tax in taxes:
            if tax.id in ext_id_map:
                tax_categ = self._l10n_nl_get_tax_categ(ext_id_map, tax)
                if tax_categ:
                    tax.write(
                        {"unece_type_id": utype_id, "unece_categ_id": tax_categ.id}
                    )

    @api.model
    def _l10n_nl_get_tax_categ(self, ext_id_map, tax):
        return (
            self.env.ref(ext_id_map[tax.id], False) or self.env["account.tax.template"]
        ).unece_categ_id

    @api.model
    def _l10n_nl_get_external_tax_id_map(self, taxes):
        tax_data = self.env["ir.model.data"].search_read(
            [("model", "=", "account.tax"), ("res_id", "in", taxes.ids)],
            ["module", "name", "res_id"],
        )
        res_map_dict = {}
        for item in tax_data:
            res_map_dict[item["res_id"]] = "%s.%s" % (
                item["module"],
                item["name"].split("_", 1)[1],
            )
        return res_map_dict
