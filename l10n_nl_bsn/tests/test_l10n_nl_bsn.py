# Copyright 2017-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestBsn(TransactionCase):
    def setUp(self):
        super().setUp()

        self.partner_bsn = self.env["res.partner"].create(
            {
                "name": "Partner with BSN",
                "company_id": self.env.company.id,
            }
        )

    def test_01_bsn_not_valid(self):
        self.partner_bsn.bsn_number = "123"
        res = self.partner_bsn.onchange_bsn_number()
        self.assertEqual(self.partner_bsn.bsn_number, "0000.00.123")
        warning = res.get("warning")
        self.assertTrue(warning)
        message = warning.get("message")
        self.assertTrue(message)
        msg_txt = "The BSN you entered (0000.00.123) is not valid."
        self.assertEqual(message, msg_txt)
        title = warning.get("title")
        self.assertTrue(title)
        self.assertEqual(title, "Warning!")

    def test_02_bsn_valid(self):
        self.partner_bsn.bsn_number = "100000009"
        res = self.partner_bsn.onchange_bsn_number()
        self.assertEqual(self.partner_bsn.bsn_number, "1000.00.009")
        warning = res.get("warning")
        self.assertFalse(warning)

    def test_03_bsn_another_partner(self):
        new_partner_bsn = self.env["res.partner"].create(
            {
                "name": "Partner with BSN - NEW",
                "bsn_number": "1000.00.009",
                "company_id": self.env.company.id,
            }
        )
        self.partner_bsn.bsn_number = "100000009"
        res = self.partner_bsn.onchange_bsn_number()
        self.assertTrue(res.get("warning"))
        warning = new_partner_bsn._warn_bsn_existing()
        message = warning.get("message")
        self.assertTrue(message)
        msg_txt = (
            "Another person (Partner with BSN - NEW) has the same BSN (1000.00.009)."
        )
        self.assertEqual(message, msg_txt)
        self.assertEqual(message, res["warning"]["message"])
        title = warning.get("title")
        self.assertTrue(title)
        self.assertEqual(title, "Warning!")
        self.assertEqual(title, res["warning"]["title"])

    def test_04_search_bsn_number(self):
        self.partner_bsn.bsn_number = "100000009"
        self.partner_bsn.onchange_bsn_number()
        self.partner_bsn.write({})
        self.assertEqual(self.partner_bsn.bsn_number, "1000.00.009")

        res = self.env["res.partner"].search([("bsn_number", "=", "100000009")])
        self.assertEqual(len(res), 1)
        res = self.env["res.partner"].search([("bsn_number", "=", "1000.00.009")])
        self.assertEqual(len(res), 1)
        res = self.env["res.partner"].search([("bsn_number", "ilike", "1000.00.00")])
        self.assertEqual(len(res), 1)
        res = self.env["res.partner"].search([("bsn_number", "ilike", "00.00.009")])
        self.assertEqual(len(res), 1)
        res = self.env["res.partner"].search([("bsn_number", "ilike", "00.00.00")])
        self.assertEqual(len(res), 1)
        res = self.env["res.partner"].search([("bsn_number", "=", "10000000")])
        self.assertFalse(res)
        res = self.env["res.partner"].search([("bsn_number", "=", "1000.00.00")])
        self.assertFalse(res)
