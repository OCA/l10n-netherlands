# Copyright 2016-2022 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestL10nNlPartnerName(TransactionCase):
    def test_l10n_nl_partner_name(self):
        partner = self.env["res.partner"].create({"name": "Mark Rutte"})
        self.assertEqual(partner.firstname, "Mark")
        self.assertEqual(partner.lastname, "Rutte")
        partner.firstname = "Willem-Alexander"
        partner.lastname = "van Oranje-Nassau"
        self.assertEqual(partner.name, "Willem-Alexander van Oranje-Nassau")
        partner.name = partner.name
        self.assertEqual(partner.firstname, "Willem-Alexander")
        self.assertEqual(partner.infix, "van")
        self.assertEqual(partner.lastname, "Oranje-Nassau")
        self.assertEqual(partner.name, "Willem-Alexander van Oranje-Nassau")
        partner.name = "Willem Frederik (W.F.) Hermans"
        self.assertEqual(partner.firstname, "Willem Frederik")
        self.assertEqual(partner.infix, "")
        self.assertEqual(partner.initials, "W.F.")
        self.assertEqual(partner.lastname, "Hermans")
        self.assertEqual(partner.name, "Willem Frederik (W.F.) Hermans")
        partner.name = "Alfred J. Kwack"
        self.assertEqual(partner.firstname, "Alfred")
        self.assertEqual(partner.infix, "")
        self.assertEqual(partner.initials, "J.")
        self.assertEqual(partner.lastname, "Kwack")
        partner.write({"initials": "A.J."})
        self.assertEqual(partner.name, "Alfred (A.J.) Kwack")
        partner.name = "Willem-Alexander van Oranje Nassau"
        self.assertEqual(partner.lastname, "Oranje Nassau")
        self.env["ir.config_parameter"].set_param(
            "l10n_nl_partner_name_infixes", "von der, van"
        )
        partner.name = "Ursula von der Leyen"
        self.assertEqual(partner.lastname, "Leyen")
        self.assertEqual(partner.firstname, "Ursula")
        self.assertEqual(partner.infix, "von der")
        partner.name = "Willem-Alexander van Oranje Nassau"
        self.assertEqual(partner.lastname, "Oranje Nassau")
