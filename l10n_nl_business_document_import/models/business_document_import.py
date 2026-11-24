# Copyright 2022 bosd
# @author: bosd <c5e2fd43-d292-4c90-9d1f-74ff3436329a@anonaddy.me>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression

# Peppol Electronic Address Scheme codes used in the Netherlands, see
# EAS_MAPPING in account_edi_ubl_cii: {"NL": {"0106": None, "0190": None}}
EAS_BY_KEY = {
    "l10n_nl_kvk": "0106",
    "l10n_nl_oin": "0190",
}


class BusinessDocumentImport(models.AbstractModel):
    _inherit = "business.document.import"

    @api.model
    def _l10n_nl_match_partner_peppol(self, eas, endpoint, domain, order):
        """Match a partner on a Peppol endpoint of a given scheme."""
        return self.env["res.partner"].search(
            expression.AND(
                [
                    domain,
                    [
                        ("peppol_eas", "=", eas),
                        ("peppol_endpoint", "=", endpoint),
                    ],
                ]
            ),
            order=order,
            limit=1,
        )

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
        # As of Odoo 17 the Dutch chamber of commerce number (KvK) and the
        # Organisatie-identificatienummer (OIN) are stored as the Peppol
        # endpoint, distinguished by their EAS code.
        for key, eas in EAS_BY_KEY.items():
            if partner_dict.get(key):
                partner = self._l10n_nl_match_partner_peppol(
                    eas, partner_dict[key], domain, order
                )
                if partner:
                    return partner
        return super()._hook_match_partner(partner_dict, chatter_msg, domain, order)
