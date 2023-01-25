# Copyright 2023 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime

from odoo.tests import Form

from odoo.addons.l10n_nl_tax_statement.tests.test_l10n_nl_vat_statement import (
    TestVatStatement,
)


class TestTaxStatementIcp(TestVatStatement):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        daterange_type = cls.env["date.range.type"].create({"name": "Type 1"})
        daterange_vals = {
            "name": "Daterange 1",
            "type_id": daterange_type.id,
            "date_start": "2016-01-01",
            "date_end": "2016-12-31",
        }
        cls.daterange = cls.env["date.range"].create(daterange_vals)

    def test_01_date_range(self):
        """When setting the Date Range, the From Date and To Date are updated accordingly"""
        self.assertEqual(self.statement_1.state, "draft")
        self.assertNotEqual(self.statement_1.from_date, datetime.date(2016, 1, 1))
        self.assertNotEqual(self.statement_1.to_date, datetime.date(2016, 12, 31))

        # setting the date range modifies the From Date and To Date
        form = Form(self.statement_1)
        form.date_range_id = self.daterange
        form.save()
        self.assertEqual(self.statement_1.from_date, datetime.date(2016, 1, 1))
        self.assertEqual(self.statement_1.to_date, datetime.date(2016, 12, 31))

        # removing the date range doesn't affect the From Date and To Date
        form = Form(self.statement_1)
        form.date_range_id = self.env["date.range"]
        form.save()
        self.assertEqual(self.statement_1.from_date, datetime.date(2016, 1, 1))
        self.assertEqual(self.statement_1.to_date, datetime.date(2016, 12, 31))

    def test_02_date_range(self):
        """Setting the Date Range is allowed only when the statement is in draft"""
        self.statement_1.statement_update()
        self.statement_1.post()
        self.assertEqual(self.statement_1.state, "posted")
        self.assertNotEqual(self.statement_1.from_date, datetime.date(2016, 1, 1))
        self.assertNotEqual(self.statement_1.to_date, datetime.date(2016, 12, 31))

        # setting the date range is not allowed
        form = Form(self.statement_1)
        with self.assertRaises(AssertionError):
            form.date_range_id = self.daterange
