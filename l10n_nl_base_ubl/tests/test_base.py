# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import fields
from openerp.tests.common import HttpCase


class TestBase(HttpCase):
    def setUp(self):
        super(TestBase, self).setUp()
        partner = self.env.ref('base.res_partner_4')
        partner.country_id = self.env.ref('base.nl').id
        product = self.env.ref('product.product_product_4')
        journal = self.env.ref('account.sales_journal')
        self.invoice = self.env['account.invoice'].create({
            'type': 'out_invoice',
            'partner_id': partner.id,
            'account_id': self.env.ref('account.a_recv').id,
            'journal_id': journal.id,
            'date_invoice': fields.Date.today(),
            'invoice_line': [(0, 0, {
                'name': 'product that cost 100',
                'account_id': self.env.ref('account.a_sale').id,
                'price_unit': 100.0,
                'quantity': 1,
                'product_id': product.id,
            })],
        })
