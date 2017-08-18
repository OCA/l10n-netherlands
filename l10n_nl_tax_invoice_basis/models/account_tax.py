# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def get_move_line_partial_domain(self, from_date, to_date, company_id):
        company = self.env['res.company'].browse(company_id)
        is_nl = company.country_id == self.env.ref('base.nl')
        if is_nl:
            return [
                ('company_id', '=', company_id),
                '|',
                '&',
                ('tax_date', '!=', False),
                '&',
                ('tax_date', '<=', to_date),
                ('tax_date', '>=', from_date),
                '&',
                ('tax_date', '=', False),
                '&',
                ('date', '<=', to_date),
                ('date', '>=', from_date),
            ]
        return super(AccountTax, self).get_move_line_partial_domain(
            from_date,
            to_date,
            company_id
        )
