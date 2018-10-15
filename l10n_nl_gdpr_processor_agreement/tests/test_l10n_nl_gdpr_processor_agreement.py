# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestL10nNlGdprProcessorAgreement(TransactionCase):
    def test_l10n_nl_gdpr_processor_agreement(self):
        self.assertEqual(
            self.env.ref('base.main_partner').data_protection_officer_id,
            self.env.ref('base.res_partner_main1')
        )
