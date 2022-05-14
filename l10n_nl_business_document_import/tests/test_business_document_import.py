# Copyright 2022 bosd
# @author: bosd <c5e2fd43-d292-4c90-9d1f-74ff3436329a@anonaddy.me>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class Testl10nNLBusinessDocumentImport(TransactionCase):
    def test_match_partner_coc_oin(self):
        partner1 = self.env["res.partner"].create(
            {
                "name": "Onestein",
                "supplier_rank": 1,
                "is_company": True,
                "coc_registration_number": "56048785",
            }
        )
        partner2 = self.env["res.partner"].create(
            {
                "name": "Partner with OIN",
                "supplier_rank": 1,
                "is_company": True,
                "nl_oin": "12345678901234567890",
            }
        )
        bdio = self.env["business.document.import"]
        partner_dict = {"coc_registration_number": "56048785"}
        res = bdio._match_partner(partner_dict, [])
        self.assertIn(res, [partner1, partner2])
        partner_dict = {"coc_registration_number": "56048785"}
        res = bdio._match_partner(partner_dict, [])
        self.assertEqual(res, partner1)
        partner_dict = {"nl_oin": "12345678901234567890"}
        res = bdio._match_partner(partner_dict, [])
        self.assertIn(res, [partner1, partner2])

    def test_nomatch_partner_coc_oin(self):
        bdio = self.env["business.document.import"]
        partner_dict = {
            "name": "ready mat ",
            "nl_oin": "",
            "coc_registration_number": "",
        }
        partner_ready_mat = self.env.ref("base.res_partner_4")
        res = bdio._match_partner(partner_dict, [])
        self.assertEqual(res, partner_ready_mat)
