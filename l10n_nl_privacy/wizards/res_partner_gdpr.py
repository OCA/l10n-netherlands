# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
from openerp import api, models


class ResPartnerGdpr(models.TransientModel):
    _inherit = 'res.partner.gdpr'

    @api.multi
    def _pre_gdpr_cleanup(self):
        """Go through all the invoices created by the partners that are about
        to be "cleaned", print any reports that might exist for the invoice
        model and attach them as attachments to the records.
        """
        self.ensure_one()
        for partner_id in self.partner_ids:
            self._save_account_invoice_reports(partner_id)
            self._save_sale_order_reports(partner_id)
            self._save_stock_picking_reports(partner_id)
        return super(ResPartnerGdpr, self)._pre_gdpr_cleanup()

    def _save_reports(self, partner_id, model_name):
        for invoice in self.env[model_name].search([
                ('partner_id', '=', partner_id.id)]):
            for report in self.env['ir.actions.report.xml'].search([
                    ('model', '=', model_name)]):
                pdf = self.pool['report'].get_pdf(
                    self.env.cr,
                    self.env.uid,
                    invoice.ids,
                    report.report_name,
                    context={}
                )
                self.env['ir.attachment'].create({
                    'name': report.report_name.replace('.', '') + '.pdf',
                    'datas': base64.encodestring(pdf),
                    'res_model': model_name,
                    'res_id': invoice.id,
                })

    def _save_account_invoice_reports(self, partner_id):
        self._save_reports(partner_id, 'account.invoice')

    def _save_sale_order_reports(self, partner_id):
        self._save_reports(partner_id, 'sale.order')

    def _save_stock_picking_reports(self, partner_id):
        self._save_reports(partner_id, 'stock.picking')
