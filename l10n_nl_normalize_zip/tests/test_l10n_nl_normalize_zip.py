# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestL10nNlNormalizeZip(TransactionCase):
    def test_l10n_nl_normalize_zip(self):
        partner = self.env['res.partner'].create({
            'name': 'testpartner',
        })
        self.assertEqual(partner.zip, False)
        partner.write({
            'zip': u'should be unchanged',
        })
        self.assertEqual(partner.zip, 'should be unchanged')
        partner.write({
            'zip': '1053nj',
        })
        self.assertEqual(partner.zip, '1053 NJ')
