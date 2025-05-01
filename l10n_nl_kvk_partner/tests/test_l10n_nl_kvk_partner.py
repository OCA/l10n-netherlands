# Copyright 2025 360ERP (<https://www.360erp.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestL10nNlKvkPartner(BaseCommon):
    def _create_partner(self, vals=None):
        """Convenience method to create a Dutch company partner"""
        base_vals = {
            "company_type": "company",
            "country_id": self.env.ref("base.nl").id,
            "name": "Partner 1",
        }
        base_vals.update(vals or {})
        return self.env["res.partner"].create(base_vals)

    def _get_partner_form(self):
        """Convenience method to create a form for a Dutch company partner"""
        partner_form = Form(self.env["res.partner"])
        partner_form.company_type = "company"
        partner_form.country_id = self.env.ref("base.nl")
        partner_form.name = "Partner 1"
        return partner_form

    def test_create_kvk(self):
        partner = self._create_partner({"l10n_nl_kvk": "99876543"})
        self.assertRecordValues(
            partner,
            [
                {
                    "l10n_nl_kvk": "99876543",
                    "peppol_eas": "0106",
                    "peppol_endpoint": "99876543",
                },
            ],
        )
        self.assertIn(
            partner, self.env["res.partner"].search([("l10n_nl_kvk", "like", "987")])
        )
        self.assertNotIn(
            partner, self.env["res.partner"].search([("l10n_nl_kvk", "like", "9999")])
        )

    def test_create_kvk_form(self):
        partner_form = self._get_partner_form()
        partner_form.l10n_nl_kvk = "99876543"
        self.assertRecordValues(
            partner_form.save(),
            [
                {
                    "l10n_nl_kvk": "99876543",
                    "peppol_eas": "0106",
                    "peppol_endpoint": "99876543",
                },
            ],
        )

    def test_create_peppol(self):
        partner = self._create_partner(
            {
                "peppol_eas": "0106",
                "peppol_endpoint": "99876543",
            }
        )
        self.assertRecordValues(
            partner,
            [
                {
                    "l10n_nl_kvk": "99876543",
                    "peppol_eas": "0106",
                    "peppol_endpoint": "99876543",
                },
            ],
        )
        self.assertIn(
            partner, self.env["res.partner"].search([("l10n_nl_kvk", "like", "987")])
        )

    def test_create_peppol_form(self):
        partner_form = self._get_partner_form()
        partner_form.peppol_endpoint = "99876543"
        partner_form.peppol_eas = "0106"
        self.assertRecordValues(
            partner_form.save(),
            [
                {
                    "l10n_nl_kvk": "99876543",
                    "peppol_eas": "0106",
                    "peppol_endpoint": "99876543",
                },
            ],
        )

    def test_create_no_kvk(self):
        partner = self._create_partner(
            {
                "peppol_eas": "0190",
                "peppol_endpoint": "2.16.528.1.1007",
            }
        )
        self.assertRecordValues(
            partner,
            [
                {
                    "l10n_nl_kvk": False,
                    "peppol_eas": "0190",
                    "peppol_endpoint": "2.16.528.1.1007",
                },
            ],
        )
        self.assertNotIn(
            partner,
            self.env["res.partner"].search([("l10n_nl_kvk", "like", "528")]),
        )

    def test_create_no_kvk_form(self):
        partner_form = self._get_partner_form()
        partner_form.peppol_endpoint = "2.16.528.1.1007"
        partner_form.peppol_eas = "0190"
        self.assertRecordValues(
            partner_form.save(),
            [
                {
                    "l10n_nl_kvk": False,
                    "peppol_eas": "0190",
                    "peppol_endpoint": "2.16.528.1.1007",
                },
            ],
        )
