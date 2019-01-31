# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CreditControlPolicy(models.Model):
    _inherit = 'credit.control.policy'

    fee_tax_ids = fields.Many2many(
        comodel_name='account.tax',
        string='Fee Taxes'
    )

    min_fee = fields.Monetary(
        string='Minimum Fee',
        default=40
    )

    max_fee = fields.Monetary(
        string='Maximum Fee',
        default=6775
    )

    fee_ids = fields.One2many(
        string='Fees',
        comodel_name='credit.control.policy.fee',
        inverse_name='credit_control_policy_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id
    )

    @api.multi
    def calculate_fee(self, amount):
        fee = 0
        for fee_record in self.fee_ids:
            tmp_amount = amount - fee_record.amount

            if tmp_amount < 0:
                fee += amount * fee_record.fee_percentage
                break
            else:
                fee += fee_record.amount * fee_record.fee_percentage
                amount -= fee_record.amount
        if fee > self.max_fee:
            fee = self.max_fee
        elif fee < self.min_fee:
            fee = self.min_fee
        return fee
