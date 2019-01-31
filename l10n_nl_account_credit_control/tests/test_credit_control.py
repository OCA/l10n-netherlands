# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestCreditControl(TransactionCase):
    def test_fee_calculation(self):
        policy = self.env.ref('account_credit_control.credit_control_3_time')

        # Test minimal amount
        self.assertEqual(policy.calculate_fee(5), policy.min_fee)

        # Test 1 tier fee
        self.assertEqual(policy.calculate_fee(1500), 225)

        # Test 2 tier fee
        self.assertEqual(policy.calculate_fee(3000), 425)

        # Test 3 tier fee
        self.assertEqual(policy.calculate_fee(800000), 5775)

        # Test maximum amount
        self.assertEqual(policy.calculate_fee(1200000), policy.max_fee)

    def test_communication(self):
        partner = self.env.ref('base.main_partner')
        level = self.env.ref('account_credit_control.3_time_1')
        currency = self.env.ref('base.USD')
        level.custom_text = '#FEE#'
        level.custom_text_after_details = '#FEENOTAX#'
        level.custom_mail_text = '#FEETAX#'

        comm = self.env['credit.control.communication'].create({
            'currency_id': currency.id,
            'partner_id': partner.id,
            'current_policy_level': level.id
        })
        self.assertTrue('#FEE#' not in comm.custom_text)
        self.assertTrue('#FEENOTAX#' not in comm.custom_text_after_details)
        self.assertTrue('#FEETAX#' not in comm.custom_mail_text)
