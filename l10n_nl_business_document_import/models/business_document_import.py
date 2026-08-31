# Copyright 2022 bosd
# @author: bosd <c5e2fd43-d292-4c90-9d1f-74ff3436329a@anonaddy.me>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class BusinessDocumentImport(models.AbstractModel):
    _inherit = "business.document.import"

    @api.model
    def _hook_match_partner(self, partner_dict, chatter_msg, domain, order):
        rpo = self.env["res.partner"]
        if partner_dict.get("company_registry"):
            company_registry = partner_dict["company_registry"]
            partner = rpo.search(
                expression.AND([domain, [("company_registry", "=", company_registry)]]),
                order=order,
                limit=1,
            )
            if partner:
                return partner
        # l10n_nl_oin is an optional dependency: only match on the OIN when
        # that module happens to be installed.
        if "l10n_nl_oin" in rpo._fields and partner_dict.get("l10n_nl_oin"):
            partner = rpo.search(
                expression.AND(
                    [
                        domain,
                        [
                            ("parent_id", "=", False),
                            ("l10n_nl_oin", "=", partner_dict["l10n_nl_oin"]),
                        ],
                    ]
                ),
                order=order,
                limit=1,
            )
            if partner:
                return partner
        return super()._hook_match_partner(partner_dict, chatter_msg, domain, order)
