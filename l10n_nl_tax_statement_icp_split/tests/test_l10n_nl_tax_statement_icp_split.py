# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.addons.l10n_nl_tax_statement.tests import test_l10n_nl_vat_statement


class TestL10nNlVatStatementIcpSplit(test_l10n_nl_vat_statement.TestVatStatement):
    def test_icp_statement(self):
        self._create_test_invoice()
        self.invoice_1.invoice_line_ids.tax_tag_ids = self.tag_5
        self.invoice_1._post()

        icp_statement = self.env["l10n.nl.icp.statement"].create({})
        icp_statement.statement_update()
        self.assertTrue(icp_statement.icp_line_ids_has_errors)

        icp_statement.reset()
        self.assertFalse(icp_statement.icp_line_ids)

        self.invoice_1.partner_id.country_id = self.env.ref("base.be")
        self.invoice_1.partner_id.vat = "BE0477472701"
        icp_statement.statement_update()
        self.assertFalse(icp_statement.icp_line_ids_has_errors)

        move = self.invoice_1.copy(
            {
                "move_type": "entry",
                "partner_id": False,
                "date": self.invoice_1.date,
            }
        )
        move.line_ids.partner_id = None
        move.line_ids.tax_tag_ids = self.tag_5
        move._post()
        icp_statement.statement_update()
        self.assertTrue(icp_statement.icp_line_ids_has_errors)
        icp_statement.reset()
        move.button_cancel()
        icp_statement.statement_update()
        icp_statement.post()
        action = icp_statement.icp_line_ids.view_tax_lines()
        self.assertEqual(
            self.env[action["res_model"]].search(action["domain"]).move_id,
            self.invoice_1,
        )
