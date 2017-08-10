# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.tests.common import TransactionCase


class TestIntrastatNL(TransactionCase):
    """Tests for this module"""

    def setUp(self):
        super(TestIntrastatNL, self).setUp()
        self.intrastat_report = self.env['l10n_nl.report.intrastat']

    def test_generate_report(self):
        # Set our company's country to NL
        company = self.env.ref('base.main_company')
        company.country_id = self.env.ref('base.nl')
        # Create an empty, draft intrastat report
        report = self.intrastat_report.create({
            'company_id': company.id
        })
        self.assertEquals(report.state, 'draft')
        # Check if the period has correctly defaulted to last month
        a_date_in_last_month = datetime.today() \
            + relativedelta(day=1, months=-1)
        period_name = datetime.strftime(a_date_in_last_month, 'X %m/%Y')
        self.assertEquals(report.period_id.name, period_name)
        # Generate lines and store initial total
        report.generate_lines()
        total = report.total_amount
        # Product: On site Monitoring, a service
        product = self.env.ref('product.product_product_1')
        # Create a new invoice to MediaPole (de), dated last month.
        # Total price: 250
        invoice = self.env['account.invoice'].create({
            'account_id': self.env.ref('account.a_recv').id,
            'date_invoice': a_date_in_last_month,
            'partner_id': self.env.ref('base.res_partner_8').id,
            'invoice_line': [
                (0, False, {
                    'name': 'Test sale',
                    'account_id': self.env.ref('account.a_sale').id,
                    'price_unit': 50.0,
                    'product_id': product.id,
                    'quantity': 5.0,
                    'uos_id': self.env.ref('product.product_uom_unit').id
                })
            ]
        })
        # validate the invoice
        invoice.signal_workflow('invoice_open')
        # generate lines again
        report.set_draft()
        report.generate_lines()
        # Test if the difference between the previous and current amount is 250
        self.assertEquals(report.total_amount - total, 250.0)
