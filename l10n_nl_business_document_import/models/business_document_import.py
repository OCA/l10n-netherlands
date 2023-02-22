# Copyright 2022 bosd
# @author: bosd <c5e2fd43-d292-4c90-9d1f-74ff3436329a@anonaddy.me>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class BusinessDocumentImport(models.AbstractModel):
    _inherit = "business.document.import"

    @api.model
    def _hook_match_partner(self, partner_dict, chatter_msg, domain, order):
        rpo = self.env["res.partner"]
        if partner_dict.get("coc_registration_number"):
            partner_coc = partner_dict["coc_registration_number"]
            partner = rpo.search(
                domain + [("coc_registration_number", "=", partner_coc)],
                order=order,
                limit=1,
            )
            if partner:
                return partner
        if partner_dict.get("nl_oin"):
            nl_oin = partner_dict["nl_oin"]
            partner = rpo.search(
                domain
                + [
                    ("parent_id", "=", False),
                    ("nl_oin", "=", nl_oin),
                ],
                limit=1,
                order=order,
            )
            if partner:
                return partner
        return super()._hook_match_partner(partner_dict, chatter_msg, domain, order)
