# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.misc import formatLang


class CreditControlCommunication(models.TransientModel):
    _inherit = 'credit.control.communication'

    fee = fields.Monetary(compute='_compute_fee',
                          currency_field='currency_id')
    fee_without_tax = fields.Monetary(compute='_compute_fee',
                                      currency_field='currency_id')
    fee_tax = fields.Monetary(compute='_compute_fee',
                              currency_field='currency_id')
    custom_text = fields.Text(compute='_compute_fee')
    custom_text_after_details = fields.Text(compute='_compute_fee')
    custom_mail_text = fields.Html(compute='_compute_fee')

    @api.multi
    @api.depends('total_due')
    def _compute_fee(self):
        for comm in self:
            policy = comm.current_policy_level.policy_id
            tax = policy.fee_tax_ids
            amounts = tax.compute_all(policy.calculate_fee(comm.total_due))
            comm.fee = amounts['total_included']
            comm.fee_without_tax = amounts['total_excluded']
            comm.fee_tax = amounts['total_included'] - amounts[
                'total_excluded']

            replaces = {
                '#FEE#': formatLang(
                    self.env, comm.fee, monetary=True,
                    currency_obj=comm.currency_id),
                '#FEENOTAX#': formatLang(
                    self.env, comm.fee_without_tax, monetary=True,
                    currency_obj=comm.currency_id),
                '#FEETAX#': formatLang(
                    self.env, comm.fee_tax, monetary=True,
                    currency_obj=comm.currency_id)
            }.items()

            comm.custom_text = comm.current_policy_level.custom_text
            if comm.custom_text:
                for key, value in replaces:
                    comm.custom_text = comm.custom_text.replace(key, value)

            comm.custom_text_after_details = comm.current_policy_level.\
                custom_text_after_details
            if comm.custom_text_after_details:
                for key, value in replaces:
                    comm.custom_text_after_details = \
                        comm.custom_text_after_details.replace(key, value)

            comm.custom_mail_text = comm.current_policy_level.custom_mail_text
            if comm.custom_mail_text:
                for key, value in replaces:
                    comm.custom_mail_text = \
                        comm.custom_mail_text.replace(key, value)
