# Copyright 2022 bosd
# @author: bosd <c5e2fd43-d292-4c90-9d1f-74ff3436329a@anonaddy.me>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

KVK = "56048785"
OIN = "12345678901234567890"


class Testl10nNLBusinessDocumentImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bdio = cls.env["business.document.import"]
        cls.nl = cls.env.ref("base.nl")
        cls.partner_registry = cls.env["res.partner"].create(
            {
                "name": "Onestein",
                "supplier_rank": 1,
                "is_company": True,
                "country_id": cls.nl.id,
                "company_registry": KVK,
            }
        )
        cls.partner_kvk = cls._create_peppol_partner("Partner with KvK", "0106", KVK)
        cls.partner_oin = cls._create_peppol_partner("Partner with OIN", "0190", OIN)

    @classmethod
    def _create_peppol_partner(cls, name, eas, endpoint):
        return cls.env["res.partner"].create(
            {
                "name": name,
                "supplier_rank": 1,
                "is_company": True,
                "country_id": cls.nl.id,
                "peppol_eas": eas,
                "peppol_endpoint": endpoint,
            }
        )

    def test_match_partner_company_registry(self):
        res = self.bdio._match_partner({"company_registry": KVK}, [])
        self.assertEqual(res, self.partner_registry)

    def test_match_partner_kvk(self):
        """The KvK number is matched on the Peppol endpoint with EAS 0106."""
        res = self.bdio._match_partner({"l10n_nl_kvk": KVK}, [])
        self.assertEqual(res, self.partner_kvk)

    def test_match_partner_oin(self):
        """The OIN is matched on the Peppol endpoint with EAS 0190."""
        res = self.bdio._match_partner({"l10n_nl_oin": OIN}, [])
        self.assertEqual(res, self.partner_oin)

    def test_match_partner_eas_is_significant(self):
        """The same number under another EAS must not match."""
        res = self.bdio._match_partner({"name": "Onestein", "l10n_nl_oin": KVK}, [])
        self.assertEqual(res, self.partner_registry)

    def test_match_partner_company_registry_wins(self):
        """The company registry is matched before the Peppol endpoint."""
        res = self.bdio._match_partner(
            {"company_registry": KVK, "l10n_nl_kvk": KVK}, []
        )
        self.assertEqual(res, self.partner_registry)

    def test_match_partner_unknown_company_registry(self):
        """An unknown company registry falls through to the standard matching."""
        res = self.bdio._match_partner(
            {"name": "Onestein", "company_registry": "99999999"}, []
        )
        self.assertEqual(res, self.partner_registry)

    def test_match_partner_unknown_kvk(self):
        """An unknown KvK number falls through to the standard matching."""
        res = self.bdio._match_partner(
            {"name": "Onestein", "l10n_nl_kvk": "99999999"}, []
        )
        self.assertEqual(res, self.partner_registry)

    def test_nomatch_partner(self):
        """Empty values fall through to the regular name matching."""
        partner_dict = {
            "name": "onestein ",
            "company_registry": "",
            "l10n_nl_kvk": "",
            "l10n_nl_oin": "",
        }
        res = self.bdio._match_partner(partner_dict, [])
        self.assertEqual(res, self.partner_registry)
