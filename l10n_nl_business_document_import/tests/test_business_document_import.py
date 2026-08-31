# Copyright 2022 bosd
# @author: bosd <c5e2fd43-d292-4c90-9d1f-74ff3436329a@anonaddy.me>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class Testl10nNLBusinessDocumentImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bdio = cls.env["business.document.import"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Onestein",
                "supplier_rank": 1,
                "is_company": True,
                "company_registry": "56048785",
            }
        )

    def _skip_without_oin(self):
        if "l10n_nl_oin" not in self.env["res.partner"]._fields:  # pragma: no cover
            self.skipTest("l10n_nl_oin is not installed")

    def _create_oin_partner(self):
        return self.env["res.partner"].create(
            {
                "name": "Partner with OIN",
                "supplier_rank": 1,
                "is_company": True,
                "l10n_nl_oin": "12345678901234567890",
            }
        )

    def test_match_partner_coc(self):
        res = self.bdio._match_partner({"company_registry": "56048785"}, [])
        self.assertEqual(res, self.partner)

    def test_match_partner_oin(self):
        self._skip_without_oin()
        partner_oin = self._create_oin_partner()
        res = self.bdio._match_partner({"l10n_nl_oin": "12345678901234567890"}, [])
        self.assertEqual(res, partner_oin)

    def test_match_partner_coc_wins_over_oin(self):
        """The CoC number is matched before the OIN."""
        self._skip_without_oin()
        self._create_oin_partner()
        res = self.bdio._match_partner(
            {
                "company_registry": "56048785",
                "l10n_nl_oin": "12345678901234567890",
            },
            [],
        )
        self.assertEqual(res, self.partner)

    def test_match_partner_unknown_coc(self):
        """An unknown CoC number falls through to the standard matching."""
        res = self.bdio._match_partner(
            {"name": "Onestein", "company_registry": "99999999"}, []
        )
        self.assertEqual(res, self.partner)

    def test_match_partner_unknown_oin(self):
        """An unknown OIN falls through to the standard matching."""
        self._skip_without_oin()
        res = self.bdio._match_partner(
            {"name": "Onestein", "l10n_nl_oin": "99999999999999999999"}, []
        )
        self.assertEqual(res, self.partner)

    def test_nomatch_partner_coc_oin(self):
        """Empty CoC/OIN values fall through to the regular name matching."""
        partner_dict = {
            "name": "onestein ",
            "l10n_nl_oin": "",
            "company_registry": "",
        }
        res = self.bdio._match_partner(partner_dict, [])
        self.assertEqual(res, self.partner)
