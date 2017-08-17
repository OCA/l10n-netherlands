# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        self.ensure_one()
        move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(
            move_lines
        )
        for line in filter(lambda l: l[2]['tax_line_id'], move_lines):
            line[2]['tax_date'] = self.date_invoice
        return move_lines
