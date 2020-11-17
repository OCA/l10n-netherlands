# -*- coding: utf-8 -*-
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from openerp import api, models


class BaseUbl(models.AbstractModel):
    _inherit = "base.ubl"

    @api.model
    def _ubl_add_party_legal_entity(self, partner, parent_node, ns, version="2.1"):
        """ Add NL-specific things to PartyLegalEntity """
        res = super(BaseUbl, self)._ubl_add_party_legal_entity(
            partner, parent_node, ns, version=version
        )

        # Check if we need to do Dutch modifications
        # TODO: Change this to default False
        use_dutch_ubl = self.env.context.get('l10n_nl_base_ubl_use_dutch_ubl', True)
        if not use_dutch_ubl:
            return res

        # PartyLegalEntity/CompanyID must be added just after RegistrationName
        party_legal_entity = parent_node.find(ns["cac"] + "PartyLegalEntity")
        registration_name = party_legal_entity.find(ns["cbc"] + "RegistrationName")
        id_dict = self._l10n_nl_base_ubl_get_party_identification(partner)
        if id_dict:
            for scheme_id, party_id_text in id_dict.iteritems():
                company_id = etree.Element(
                    ns["cbc"] + "CompanyID", schemeID=scheme_id
                )
                company_id.text = party_id_text
                registration_name.addnext(company_id)
        return res

    @api.model
    def _l10n_nl_base_ubl_use_dutch_ubl(self, partner):
        """ Returns True when we should use Dutch UBL dialect for this partner """
        return partner.country == self.env.ref('base.nl')

    @api.model
    def _l10n_nl_base_ubl_get_party_identification(self, commercial_partner):
        """ Unfortunately cannot use _ubl_get_party_identification,
            because it uses schemeName and we need schemeID """
        oin = self._l10n_nl_base_ubl_get_oin(commercial_partner)
        kvk = self._l10n_nl_base_ubl_get_kvk(commercial_partner)
        res = {}
        # OIN (0190) trumps KVK number (0106) if it is filled for a partner
        if oin:
            res["0190"] = oin
        elif kvk:
            res["0106"] = kvk
        return res

    @api.model
    def _ubl_add_party_identification(
            self, commercial_partner, parent_node, ns, version='2.1'):
        """ Override PartyIdentification with Dutch version """

        # Check if we need to do Dutch modifications
        # TODO: Change this to default False
        use_dutch_ubl = self.env.context.get('l10n_nl_base_ubl_use_dutch_ubl', True)
        if not use_dutch_ubl:
            return super(BaseUbl, self)._ubl_add_party_identification(
                self, commercial_partner, parent_node, ns, version=version)

        # Add PartyIdentification/ID according to KVK or OIN with correct schemeID
        id_dict = self._l10n_nl_base_ubl_get_party_identification(commercial_partner)
        if id_dict:
            party_identification = etree.SubElement(
                parent_node, ns['cac'] + 'PartyIdentification')
            for scheme_id, party_id_text in id_dict.iteritems():
                party_identification_id = etree.SubElement(
                    party_identification, ns['cbc'] + 'ID',
                    schemeID=scheme_id)
                party_identification_id.text = party_id_text

    @api.model
    def _l10n_nl_base_ubl_get_kvk(self, partner):
        """
        In case OCA module 'partner_coc' is installed, returns the value of
        field 'coc_registration_number'. Otherwise if the KvK is defined
        somewhere else you should extend this method returning its value.
        :param partner: record of commercial partner
        :return: String presenting the Dutch KvK
        """
        if partner._fields.get("coc_registration_number"):
            return partner.coc_registration_number
        return False

    @api.model
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
