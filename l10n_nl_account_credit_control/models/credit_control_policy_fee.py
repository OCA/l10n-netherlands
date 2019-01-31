# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CreditControlPolicyFee(models.Model):
    _name = 'credit.control.policy.fee'
    _order = 'sequence'

    credit_control_policy_id = fields.Many2one(
        comodel_name='credit.control.policy',
        required=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        required=True,
        related='credit_control_policy_id.currency_id'
    )

    sequence = fields.Integer()

    amount = fields.Monetary(
        string='Amount of the unpaid bill',
        currency_field='currency_id'
    )

    fee = fields.Float(
        string='Fee (%)'
    )

    fee_percentage = fields.Float(
        compute='_compute_fee_percentage'
    )

    @api.multi
    def _compute_fee_percentage(self):
        for fee in self:
            fee.fee_percentage = fee.fee / 100
