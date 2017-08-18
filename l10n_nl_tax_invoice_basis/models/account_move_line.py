# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    tax_date = fields.Date()

    date = fields.Date(
        related=False,
        compute='_compute_date',
        index=True,
        copy=False,
        store=True
    )

    @api.depends('move_id.date', 'tax_date', 'company_id.country_id')
    @api.multi
    def _compute_date(self):
        for line in self:
            line.date = line.move_id.date
            is_invoice_basis = line.company_id.l10n_nl_tax_invoice_basis
            is_nl = line.company_id.country_id == self.env.ref('base.nl')
            if is_nl and is_invoice_basis and line.tax_line_id:
                line.date = line.tax_date or line.move_id.date
