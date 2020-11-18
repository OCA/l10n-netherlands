# -*- coding: utf-8 -*-
# Copyright 2020 Sunflower IT (<https://sunflowerweb.nl>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, api
from lxml import etree
import logging

logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = ['account.invoice']

    @api.multi
    def generate_ubl_xml_string(self, version='2.1'):
        self.ensure_one()
        # If we need to do Dutch modifications, flag that in the context
        assert self.partner_id
        if self.env['base.ubl']._l10n_nl_base_ubl_use_dutch_ubl(self.partner_id):
            this = self.with_context(l10n_nl_base_ubl_use_dutch_ubl=True)
        else:
            this = self
        return super(AccountInvoice, this).generate_ubl_xml_string(version=version)

    @api.multi
    def _ubl_add_header(self, parent_node, ns, version='2.1'):
        res = super(AccountInvoice, self)._ubl_add_header(
            parent_node, ns, version=version)

        if not self.env.context.get('l10n_nl_base_ubl_use_dutch_ubl'):
            return res

        # We add CustomizationID in the header just after UBLVersionID
        ubl_version_id = parent_node.find(ns["cbc"] + "UBLVersionID")
        customization_id = etree.Element(ns["cbc"] + "CustomizationID")
        customization_id.text = \
            "urn:cen.eu:en16931:2017#compliant#urn:fdc:nen.nl:nlcius:v1.0"
        ubl_version_id.addnext(customization_id)

        return res

    def _ubl_add_invoice_line_tax_total(
            self, iline, parent_node, ns, version='2.1'):

        if not self.env.context.get('l10n_nl_base_ubl_use_dutch_ubl'):
            return super(AccountInvoice, self)._ubl_add_invoice_line_tax_total(
                iline, parent_node, ns, version=version)

        # UBL-CR-561: A UBL invoice should not include the InvoiceLine TaxTotal
        return None

    @api.model
    def _ubl_add_payment_means(
            self, partner_bank, payment_mode, date_due, parent_node, ns,
            version='2.1'):

        res = super(AccountInvoice, self)._ubl_add_payment_means(
            partner_bank, payment_mode, date_due, parent_node, ns, version=version
        )

        if not self.env.context.get('l10n_nl_base_ubl_use_dutch_ubl'):
            return res

        # UBL-CR-412: A UBL invoice should not include the PaymentMeans PaymentDueDate
        invoice = parent_node
        payment_means = invoice.find(ns['cac'] + 'PaymentMeans')
        if payment_means is not None:
            payment_due_date = payment_means.find(ns['cbc'] + 'PaymentDueDate')
            if payment_due_date is not None:
                payment_means.remove(payment_due_date)

            # UBL-CR-661: A UBL invoice should not include the PaymentMeansCode listID
            payment_means_code = payment_means.find(ns['cbc'] + 'PaymentMeansCode')
            if payment_means_code is not None:
                payment_means_code.attrib.pop("listID", None)

        return res
