# -*- coding: utf-8 -*-
# Copyright 2014-2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import api, fields, models


class AccountVatDeclaration(models.TransientModel):
    _name = 'account.vat.declaration.nl'
    _inherit = "account.common.report"

    @api.model
    def default_get(self, fields_list):
        defaults = super(AccountVatDeclaration, self).default_get(fields_list)
        company = self.env.user.company_id
        fy_dates = company.compute_fiscalyear_dates(datetime.now())
        date_from = fields.Date.to_string(fy_dates['date_from'])
        date_to = fields.Date.to_string(fy_dates['date_to'])
        defaults.setdefault('date_from', date_from)
        defaults.setdefault('date_to', date_to)
        return defaults

    @api.multi
    def create_vat(self):
        datas = {
            'form': self.read()[0],
        }
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]

        report_name = 'l10n_nl_tax_declaration_reporting.tax_report_template'

        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
        }
