# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.tests.common import TransactionCase


class TestIntrastatNL(TransactionCase):
    """Tests for this module"""

    def setUp(self):
        super(TestIntrastatNL, self).setUp()
        self.intrastat_report = self.env['l10n_nl.report.intrastat']
        self.account_receivable = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref('account.data_account_type_receivable').id)], limit=1)
        self.fiscal_position_model = self.env['account.fiscal.position']

    def test_generate_report(self):
        # Set our company's country to NL
        company = self.env.ref('base.main_company')
        company.country_id = self.env.ref('base.nl')

        # Create a date range type
        type = self.env['date.range.type'].create({
            'name': 'Test date range type',
            'company_id': company.id,
            'allow_overlap': False
        })

        # Create a date range spanning the last three months
        date_range = self.env['date.range'].create({
            'name': 'FS2016',
            'date_start': datetime.today() + relativedelta(months=-3),
            'date_end': datetime.today(),
            'company_id': company.id,
            'type_id': type.id
        })

        # Create an empty, draft intrastat report for this period
        report = self.intrastat_report.create({
            'company_id': company.id,
            'date_range_id': date_range.id,

        })
        self.assertEquals(report.state, 'draft')

        # Generate lines and store initial total
        report.generate_lines()
        total = report.total_amount

        # Create a new invoice to Camptocamp (FR), dated last month, price: 250
        # Product: On site Monitoring, a service
        product = self.env.ref('product.product_product_1')
        a_date_in_last_month = datetime.today() \
            + relativedelta(day=1, months=-1)
        fp = self.fiscal_position_model.create(dict(name="fiscal position", sequence=1))
        invoice = self.env['account.invoice'].create({
            'reference_type': 'none',
            'name': 'invoice to client',
            'account_id': self.account_receivable.id,
            'type': 'out_invoice',
            'fiscal_position_id': fp.id,
            'date_invoice': a_date_in_last_month,
            'partner_id': self.env.ref('base.res_partner_12').id,
            'invoice_line_ids': [
                (0, False, {
                    'name': 'Test sale',
                    'account_id': self.env.ref('account.demo_sale_of_land_account').id,
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

