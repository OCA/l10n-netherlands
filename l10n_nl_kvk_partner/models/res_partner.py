# Copyright 2025 360ERP (<https://www.360erp.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models

KVK_SCHEME_ID = "0106"


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_nl_kvk = fields.Char(
        "KvK Number",
        help="Dutch Chamber of Commerce number",
        compute="_compute_l10n_nl_kvk",
        inverse="_inverse_l10n_nl_kvk",
        search="_search_l10n_nl_kvk",
    )

    @api.depends("peppol_endpoint", "peppol_eas")
    def _compute_l10n_nl_kvk(self):
        """Reflect the Peppol Endpoint as the KvK Number"""
        for partner in self:
            partner.l10n_nl_kvk = (
                partner.peppol_endpoint
                if partner.peppol_eas == KVK_SCHEME_ID
                else False
            )

    def _inverse_l10n_nl_kvk(self):
        """Store the KvK number as the Peppol Endpoint and EAS"""
        for partner in self:
            if not partner.l10n_nl_kvk and partner.peppol_eas == KVK_SCHEME_ID:
                partner.peppol_endpoint = False
                partner.peppol_eas = False
            elif partner.l10n_nl_kvk:
                partner.peppol_endpoint = partner.l10n_nl_kvk
                partner.peppol_eas = KVK_SCHEME_ID

    def _search_l10n_nl_kvk(self, operator, value):
        """Translate to a search on Peppol attributes"""
        return [
            ("peppol_eas", "=", KVK_SCHEME_ID),
            ("peppol_endpoint", operator, value),
        ]
