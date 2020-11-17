# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class BaseUbl(models.AbstractModel):
    _inherit = "base.ubl"

    @api.model
    def _ubl_add_party_identification(self, partner, parent_node, ns, version="2.1"):
        res = super()._ubl_add_party_identification(
            partner, parent_node, ns, version=version
        )

        kvk = self._l10n_nl_base_ubl_get_kvk(partner)
        if kvk:
            entity = etree.SubElement(parent_node, ns["cac"] + "PartyLegalEntity")
            entity_id = etree.SubElement(
                entity, ns["cbc"] + "CompanyID", schemeID="NL:KVK", schemeAgencyID="ZZZ"
            )
            entity_id.text = kvk

        oin = self._l10n_nl_base_ubl_get_oin(partner)
        if oin:
            ident = etree.SubElement(parent_node, ns["cac"] + "PartyIdentification")
            ident_id = etree.SubElement(
                ident, ns["cbc"] + "ID", schemeID="NL:OIN", schemeAgencyID="ZZZ"
            )
            ident_id.text = oin

        return res

    def _l10n_nl_base_ubl_get_kvk(self, partner):
        """
        In case OCA module 'partner_coc' is installed, returns the value of
        field 'coc_registration_number'. Otherwise if the KvK is defined somewhere
        else you should extend this method returning its value.
        :param partner: record of commercial partner
        :return: String presenting the Dutch KvK
        """
        if partner._fields.get("coc_registration_number"):
            return partner.coc_registration_number
        return False

    def _l10n_nl_base_ubl_get_oin(self, partner):
        """
        In case OCA module 'l10n_nl_oin' is installed, returns the value of
        field 'nl_oin'. Otherwise if the OIN is defined somewhere
        else you should extend this method returning its value.
        :param partner: record of commercial partner
        :return: String presenting the Dutch OIN
        """
        if partner._fields.get("nl_oin"):
            return partner.nl_oin
        return False
