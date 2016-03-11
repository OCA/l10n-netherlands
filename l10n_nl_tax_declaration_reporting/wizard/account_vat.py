# -*- coding: utf-8 -*-
# © 2014-2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class AccountVatDeclaration(models.TransientModel):
    _name = 'account.vat.declaration.nl'
    _inherit = "account.common.report"

    @api.model
    def _get_tax(self):
        taxes = self.env['account.tax.code'].search(
            [('parent_id', '=', False),
             ('company_id', '=', self.env.user.company_id.id)],
            limit=1).ids
        return taxes and taxes[0] or False

    based_on = fields.Selection(
        [('invoices', 'Invoices'), ('payments', 'Payments')],
        'Based on', required=True, default='invoices'
    )
    chart_tax_id = fields.Many2one(
        'account.tax.code', 'Chart of Tax',
        help='Select Charts of Taxes',
        required=True,
        domain=[('parent_id', '=', False)],
        default=_get_tax
    )
    display_detail = fields.Boolean('Display Detail')

    @api.multi
    def create_vat(self):
        datas = {
            'ids': self.env.context.get('active_ids', []),
            'model': 'account.tax.code',
            'form': self.read()[0],
        }
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]

        datas['form']['company_id'] = self.env['account.tax.code'].browse(
            datas['form']['chart_tax_id']
        ).company_id.id

        report_name = 'l10n_nl_tax_declaration_reporting.tax_report_template'

        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
        }
