# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
import base64
from datetime import datetime ,date ,timedelta
from odoo.exceptions import ValidationError
import calendar
import time


class cbs_export_file(models.Model):
    _name = 'cbs.export.file'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.multi
    def get_filename(self):
        for rec in self:
            rec.filename = '%s_%s.csv' % (rec.month, rec.year)

    cbs_export_invoice = fields.Binary(string='CBS Export File', attachment=True)
    filename = fields.Char(string='Filename', size=64, compute='get_filename')
    name = fields.Char(string='Name', size=64)
    month = fields.Selection([
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December')
    ], default='01', string='Month')
    year = fields.Char('Year')
    account_invoice_ids = fields.One2many('account.invoice', 'cbs_export_id')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cbs.export.file')
        return super(cbs_export_file, self).create(vals)

    @api.one
    def get_data(self):
        self.set_invoice()
        self.export_file()

    @api.constrains('year')
    def check_year(self):
        if self.year:
            if not self.year.isdigit():
                raise ValidationError(_("Please insert a valid Year"))
            else:
                is_valid_year = '%d' % (int(self.year))
                try:
                    time.strptime(is_valid_year, '%Y')
                except ValueError:
                    raise ValidationError(_("Please insert a valid Year"))

    @api.one
    def set_invoice(self):
        days = calendar.monthrange(int(self.year), int(self.month))
        account_ids = self.env['account.invoice'].search([
            ('type', '=', 'out_invoice'),
            ('state', 'in', ['open', 'paid']),
            ('partner_id.country_id.intrastat', '=', True),
            ('partner_id.country_id.code', '!=', 'NL'),
            ('date_invoice', '>=', datetime.strptime(
                '%s-%s-%s' % (1, int(self.month), int(self.year)), '%d-%m-%Y')),
            ('date_invoice', '<=', datetime.strptime(
                '%s-%s-%s' % (days[1], int(self.month), int(self.year)), '%d-%m-%Y'))])
        if not account_ids:
            raise ValidationError(
                _("There are no invoice lines for CBS Export during month %s in year %s") % (calendar.month_name[int(self.month)], self.year)
            )
        else:
            account_ids.search([('cbs_export_id', '=', self.id)]).write(
                {'cbs_export_id': False}
            )
            account_ids.write({'cbs_export_id': self.id})

    @api.model
    def cron_get_cbs_export_file(self):
        last_month = date.today().replace(day=1) - timedelta(days=1)
        sr_ids = self.search([('month', '=', last_month.strftime("%m")), ('year', '=', last_month.strftime("%Y"))])
        if not sr_ids:
            sr_ids = self.create({'month': last_month.strftime("%m"), 'year': last_month.strftime("%Y")})
            sr_ids.message_post(
                body=_("CBS Export is created for month %s in year %s") % (calendar.month_name[int(sr_ids.month)], sr_ids.year),
                subtype='mt_comment'
            )
        sr_ids.set_invoice()
        sr_ids.export_file()

    @api.one
    def export_file(self):
        line_number = 1
        company_id = self.env.user.company_id
        cbs_export_data = str('9801')+str(
            company_id.vat or '').replace(' ','')[2:].ljust(12)+str(
            datetime.now().strftime("%Y%m").ljust(6)
        )+str(
            company_id.name or ''
        ).ljust(40)+str(" " * 6)+str(" " * 5)+str(
            datetime.now().strftime("%Y%m%d").ljust(8)
        )+str(
            datetime.now().strftime("%H%M%S").ljust(6)
        )+str(company_id.phone or '').replace(' ','')[0:15].ljust(15)+str(" " * 13)+'\n'
        for invoice_line in self.account_invoice_ids.mapped('invoice_line_ids'):
            sign_of_weight = '-'
            sign_of_invoice_value = '-'
            if invoice_line.invoice_id.amount_total_signed >= 0:
                sign_of_invoice_value = '+'
            if(invoice_line.quantity * invoice_line.product_id.weight) >= 0:
                sign_of_weight = '+'
            value = str(
                datetime.strptime(
                    invoice_line.invoice_id.date_invoice, '%Y-%m-%d'
                ).strftime("%Y%m") or ''
            ).ljust(6)+str('7')+str(
                invoice_line.company_id.vat or ''
            ).replace(' ','')[2:].ljust(12)+str(line_number).zfill(5)+str(" " * 3)+str(
                invoice_line.invoice_id.partner_id.country_id.code or ''
            ).ljust(3)+str('3')+str('0')+str('00')+str('00')+str('1')+str(
                invoice_line.product_id.intrastat_id.name or ''
            ).replace(' ','')[0:8].ljust(8)+str('00')+str(sign_of_weight)+str(
                int(invoice_line.quantity * invoice_line.product_id.weight)
            ).zfill(10)+str('+')+str('0000000000').zfill(10)+sign_of_invoice_value+str(
                int(invoice_line.price_subtotal)
            ).zfill(10)+str('+')+str('0000000000').zfill(10)
            if len(str(invoice_line.invoice_id.number or '')) < 8:
                invoice_value = str(invoice_line.invoice_id.number)+str(line_number).zfill(2)
                value += str(invoice_value).ljust(10)
            else:
                value += str(invoice_line.invoice_id.number or ' ')[:8].ljust(8)+str(line_number).zfill(2)
            value += str(" " * 3)+str(" " * 1)+str('000')+str(" " * 7)+'\n'
            line_number += 1
            cbs_export_data += value
        cbs_export_data += str('9899')+str(" " * 111)
        self.write({
            'cbs_export_invoice': base64.encodestring(cbs_export_data)
        })
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
