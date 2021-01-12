# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from dateutil.relativedelta import relativedelta

import odoo
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_resource_path
from odoo.tests import Form
from odoo.tests.common import TransactionCase
from odoo.tools import convert_file


class TestVatStatement(TransactionCase):
    def _load(self, module, *args):
        convert_file(
            self.cr,
            "l10n_nl",
            get_resource_path(module, *args),
            {},
            "init",
            False,
            "test",
            self.registry._assertion_report,
        )

    def _create_company_children(self):
        self.company_child_1 = self.env["res.company"].create(
            {
                "name": "Child 1 Company",
                "country_id": self.env.ref("base.nl").id,
                "parent_id": self.company_parent.id,
            }
        )
        self.env.user.company_id = self.company_child_1
        self.coa.try_loading()
        self.company_child_2 = self.env["res.company"].create(
            {
                "name": "Child 2 Company",
                "country_id": self.env.ref("base.be").id,
                "parent_id": self.company_parent.id,
            }
        )
        self.env.user.company_id = self.company_child_2
        self.coa.try_loading()
        self.env.user.company_id = self.company_parent

    def setUp(self):
        super().setUp()

        self.eur = self.env["res.currency"].search([("name", "=", "EUR")])
        self.coa = self.env.ref("l10n_nl.l10nnl_chart_template", False)
        self.coa = self.coa or self.env.ref(
            "l10n_generic_coa.configurable_chart_template"
        )
        self.company_parent = self.env["res.company"].create(
            {
                "name": "Parent Company",
                "country_id": self.env.ref("base.nl").id,
                "currency_id": self.eur.id,
            }
        )
        self.env.user.company_id = self.company_parent
        self.coa.try_loading()

        self.env["l10n.nl.vat.statement"].search([]).unlink()

        self.tag_1 = self.env["account.account.tag"].create(
            {
                "name": "+1a omzet",
                "applicability": "taxes",
                "country_id": self.env.ref("base.nl").id,
            }
        )
        self.tag_2 = self.env["account.account.tag"].create(
            {
                "name": "+1a btw",
                "applicability": "taxes",
                "country_id": self.env.ref("base.nl").id,
            }
        )
        self.tag_3 = self.env["account.account.tag"].create(
            {
                "name": "+2a omzet",
                "applicability": "taxes",
                "country_id": self.env.ref("base.nl").id,
            }
        )
        self.tag_4 = self.env["account.account.tag"].create(
            {
                "name": "-2a omzet",
                "applicability": "taxes",
                "country_id": self.env.ref("base.nl").id,
            }
        )
        self.tag_5 = self.env["account.account.tag"].create(
            {
                "name": "+3b omzet",
                "applicability": "taxes",
                "country_id": self.env.ref("base.nl").id,
            }
        )
        self.tag_6 = self.env["account.account.tag"].create(
            {
                "name": "+3b omzet d",
                "applicability": "taxes",
                "country_id": self.env.ref("base.nl").id,
            }
        )

        self.tax_1 = self.env["account.tax"].create({"name": "Tax 1", "amount": 21})
        self.tax_1.invoice_repartition_line_ids[0].tag_ids = self.tag_1
        self.tax_1.invoice_repartition_line_ids[1].tag_ids = self.tag_2

        self.tax_2 = self.env["account.tax"].create({"name": "Tax 2", "amount": 21})
        self.tax_2.invoice_repartition_line_ids[0].tag_ids = self.tag_3
        self.tax_2.invoice_repartition_line_ids[1].tag_ids = self.tag_4

        self.statement_1 = self.env["l10n.nl.vat.statement"].create(
            {"name": "Statement 1"}
        )

    def _create_test_invoice(self):
        journal = self.env["account.journal"].create(
            {"name": "Journal 1", "code": "Jou1", "type": "sale"}
        )
        partner = self.env["res.partner"].create({"name": "Test partner"})
        account_receivable = self.env["account.account"].create(
            {
                "user_type_id": self.env.ref("account.data_account_type_expenses").id,
                "code": "EXPTEST",
                "name": "Test expense account",
            }
        )
        invoice_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.partner_id = partner
        invoice_form.journal_id = journal
        with invoice_form.invoice_line_ids.new() as line:
            line.name = "Test line"
            line.quantity = 1.0
            line.account_id = account_receivable
            line.price_unit = 100.0
            line.tax_ids.clear()
            line.tax_ids.add(self.tax_1)
        with invoice_form.invoice_line_ids.new() as line:
            line.name = "Test line"
            line.quantity = 1.0
            line.account_id = account_receivable
            line.price_unit = 50.0
            line.tax_ids.clear()
            line.tax_ids.add(self.tax_2)
        self.invoice_1 = invoice_form.save()
        self.assertEqual(len(self.invoice_1.line_ids), 5)

    def test_01_onchange(self):
        daterange_type = self.env["date.range.type"].create({"name": "Type 1"})
        daterange = self.env["date.range"].create(
            {
                "name": "Daterange 1",
                "type_id": daterange_type.id,
                "date_start": "2016-01-01",
                "date_end": "2016-12-31",
            }
        )
        form = Form(self.statement_1)
        form.date_range_id = daterange
        statement = form.save()
        self.assertEqual(statement.from_date, datetime.date(2016, 1, 1))
        self.assertEqual(statement.to_date, datetime.date(2016, 12, 31))

        check_name = statement.company_id.name
        str_from_date = fields.Date.to_string(statement.from_date)
        str_to_date = fields.Date.to_string(statement.to_date)
        check_name += ": " + " ".join([str_from_date, str_to_date])
        self.assertEqual(statement.name, check_name)

        d_from = statement.from_date
        # by default the unreported_move_from_date is set to
        # a quarter (three months) before the from_date of the statement
        new_date = d_from + relativedelta(months=-3, day=1)
        self.assertEqual(statement.unreported_move_from_date, new_date)

        self.assertEqual(statement.btw_total, 0.0)

    def test_02_post_final(self):
        # in draft
        self.assertEqual(self.statement_1.state, "draft")
        self.statement_1.statement_update()
        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

        # first post
        self.statement_1.statement_update()
        self.statement_1.post()
        self.assertEqual(self.statement_1.state, "posted")
        self.assertTrue(self.statement_1.date_posted)

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

        # then finalize
        self.statement_1.finalize()
        self.assertEqual(self.statement_1.state, "final")
        self.assertTrue(self.statement_1.date_posted)

        with self.assertRaises(UserError):
            self.statement_1.write({"name": "Test Name Modified"})
        with self.assertRaises(UserError):
            self.statement_1.write({"state": "posted"})
        with self.assertRaises(UserError):
            self.statement_1.write({"date_posted": fields.Datetime.now()})
        with self.assertRaises(UserError):
            self.statement_1.unlink()
        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            with self.assertRaises(UserError):
                line.unlink()

        self.assertEqual(self.statement_1.btw_total, 0.0)

    def test_03_reset(self):
        self.statement_1.reset()
        self.assertEqual(self.statement_1.state, "draft")
        self.assertFalse(self.statement_1.date_posted)

        self.assertEqual(self.statement_1.btw_total, 0.0)

        self.statement_1.statement_update()
        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

    def test_04_write(self):
        self.statement_1.post()
        with self.assertRaises(UserError):
            self.statement_1.write({"name": "Test Name"})

        self.assertEqual(self.statement_1.btw_total, 0.0)

    def test_05_unlink_exception(self):
        self.statement_1.post()
        with self.assertRaises(UserError):
            self.statement_1.unlink()

    def test_06_unlink_working(self):
        self.statement_1.unlink()

    def test_07_update_exception1(self):
        self.statement_1.post()
        with self.assertRaises(UserError):
            self.statement_1.statement_update()

    def test_09_update_working(self):
        self._create_test_invoice()
        self.invoice_1.action_post()
        self.statement_1.statement_update()
        self.assertEqual(len(self.statement_1.line_ids.ids), 22)

        _1 = self.statement_1.line_ids.filtered(lambda r: r.code == "1")
        _1a = self.statement_1.line_ids.filtered(lambda r: r.code == "1a")

        self.assertEqual(len(_1), 1)
        self.assertEqual(len(_1a), 1)

        self.assertFalse(_1.format_omzet)
        self.assertFalse(_1.format_btw)
        self.assertTrue(_1.is_group)
        self.assertTrue(_1.is_readonly)

        self.assertEqual(_1a.format_omzet, "100.00")
        self.assertEqual(_1a.format_btw, "21.00")
        self.assertFalse(_1a.is_group)
        self.assertTrue(_1a.is_readonly)

        self.assertEqual(self.statement_1.btw_total, 21.0)
        self.assertEqual(self.statement_1.format_btw_total, "21.00")

    def test_10_line_unlink_exception(self):
        self.assertEqual(len(self.statement_1.line_ids.ids), 0)
        self.assertEqual(self.statement_1.btw_total, 0.0)

        self._create_test_invoice()
        self.invoice_1.action_post()
        self.statement_1.statement_update()
        self.statement_1.post()
        with self.assertRaises(UserError):
            self.statement_1.line_ids.unlink()

        self.assertEqual(len(self.statement_1.line_ids.ids), 22)
        self.assertEqual(self.statement_1.btw_total, 21.0)

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertTrue(line.is_readonly)
            with self.assertRaises(UserError):
                line.unlink()

    def test_12_undeclared_invoice(self):
        self._create_test_invoice()
        self.invoice_1.action_post()

        self.invoice_1.l10n_nl_add_move_in_statement()
        self.assertTrue(self.invoice_1.line_ids)
        for line in self.invoice_1.line_ids:
            self.assertTrue(line.l10n_nl_vat_statement_include)
        self.invoice_1.l10n_nl_unlink_move_from_statement()
        self.assertTrue(self.invoice_1.line_ids)
        for line in self.invoice_1.line_ids:
            self.assertFalse(line.l10n_nl_vat_statement_include)

        self.statement_1.statement_update()
        self.assertEqual(len(self.statement_1.line_ids.ids), 22)

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
        self.statement_1.post()
        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

        invoice2 = self.invoice_1.copy()
        invoice2.action_post()
        statement2 = self.env["l10n.nl.vat.statement"].create({"name": "Statement 2"})
        self.assertTrue(statement2.unreported_move_from_date)
        statement2.statement_update()
        statement2.unreported_move_from_date = fields.Date.today()
        self.assertFalse(statement2.unreported_move_ids)

        self.assertEqual(self.statement_1.btw_total, 21.0)
        self.assertEqual(self.statement_1.format_btw_total, "21.00")

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertTrue(line.is_readonly)

        statement2.with_context(skip_check_config_tag_3b_omzet=True).post()

        with self.assertRaises(UserError):
            invoice2.invoice_date = fields.Date.today()
        with self.assertRaises(UserError):
            invoice2.date = fields.Date.today()
        invoice_lines = invoice2.invoice_line_ids.filtered(
            lambda l: l.l10n_nl_vat_statement_id
        )
        self.assertTrue(invoice_lines)
        with self.assertRaises(UserError):
            invoice_lines[0].date = fields.Date.today()

    def test_13_no_previous_statement_posted(self):
        statement2 = self.env["l10n.nl.vat.statement"].create({"name": "Statement 2"})
        statement2.statement_update()
        with self.assertRaises(UserError):
            statement2.post()

        self.assertEqual(self.statement_1.btw_total, 0.0)
        self.assertEqual(self.statement_1.format_btw_total, "0.00")

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertFalse(line.is_readonly)

    @odoo.tests.tagged("post_install", "-at_install")
    def test_14_is_invoice_basis(self):
        company = self.statement_1.company_id
        company.l10n_nl_tax_invoice_basis = True
        self.assertTrue(self.statement_1.is_invoice_basis)
        company.l10n_nl_tax_invoice_basis = False
        self.assertFalse(self.statement_1.is_invoice_basis)

        self.assertEqual(self.statement_1.btw_total, 0.0)
        self.assertEqual(self.statement_1.format_btw_total, "0.00")

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertTrue(line.is_readonly)

    def test_15_invoice_basis_undeclared_invoice(self):
        self._create_test_invoice()
        self.invoice_1.action_post()
        self.statement_1.statement_update()
        self.assertEqual(len(self.statement_1.line_ids.ids), 22)

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

        self.statement_1.with_context(skip_check_config_tag_3b_omzet=True).post()
        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

        self.statement_1.company_id.l10n_nl_tax_invoice_basis = True

        self.statement_1.company_id.country_id = self.env.ref("base.nl")

        invoice2 = self.invoice_1.copy()
        self.assertFalse(invoice2.l10n_nl_vat_statement_id)
        self.assertFalse(invoice2.l10n_nl_vat_statement_include)
        old_date = fields.Date.from_string("2018-12-07")
        invoice2.invoice_date = invoice2.date = old_date
        invoice2.action_post()

        statement2 = self.env["l10n.nl.vat.statement"].create({"name": "Statement 2"})
        move_from_date = fields.Date.from_string("2015-07-07")
        statement2.unreported_move_from_date = move_from_date
        self.assertTrue(statement2.unreported_move_ids)
        statement2.add_all_undeclared_invoices()
        statement2.statement_update()
        self.assertTrue(statement2.unreported_move_ids)
        self.assertEqual(len(statement2.unreported_move_ids), 1)

        statement2.with_context(skip_check_config_tag_3b_omzet=True).post()

        self.assertEqual(self.statement_1.btw_total, 21.0)
        self.assertEqual(self.statement_1.format_btw_total, "21.00")

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertTrue(line.is_readonly)

        with self.assertRaises(UserError):
            invoice2.invoice_date = fields.Date.today()
        with self.assertRaises(UserError):
            invoice2.date = fields.Date.today()

    def test_16_is_not_invoice_unreported_move_from_date(self):
        self._create_test_invoice()
        self.invoice_1.action_post()
        self.statement_1.statement_update()
        self.assertEqual(len(self.statement_1.line_ids.ids), 22)
        self.statement_1.is_invoice_basis = False
        self.statement_1.with_context(skip_check_config_tag_3b_omzet=True).post()

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

        self.statement_1.company_id.l10n_nl_tax_invoice_basis = False
        self.statement_1.company_id.country_id = self.env.ref("base.nl")

        invoice2 = self.invoice_1.copy()
        d_date = fields.Date.from_string("2016-07-07")
        old_date = d_date + relativedelta(months=-4, day=1)
        invoice2.date = invoice2.invoice_date = old_date
        invoice2.action_post()

        statement2 = self.env["l10n.nl.vat.statement"].create({"name": "Statement 2"})
        move_from_date = fields.Date.from_string("2015-07-07")
        statement2.unreported_move_from_date = move_from_date
        statement2.statement_update()
        statement2.with_context(skip_check_config_tag_3b_omzet=True).post()

        self.assertTrue(statement2.unreported_move_ids)
        self.assertEqual(len(statement2.unreported_move_ids), 1)

        self.assertEqual(self.statement_1.btw_total, 21.0)
        self.assertEqual(self.statement_1.format_btw_total, "21.00")

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertTrue(line.is_readonly)

    def test_17_is_not_invoice_basis_undeclared_invoice(self):
        self._create_test_invoice()
        self.invoice_1.action_post()
        self.statement_1.statement_update()
        self.assertEqual(len(self.statement_1.line_ids.ids), 22)
        self.statement_1.is_invoice_basis = False
        self.statement_1.with_context(skip_check_config_tag_3b_omzet=True).post()

        self.statement_1.company_id.l10n_nl_tax_invoice_basis = False
        self.statement_1.company_id.country_id = self.env.ref("base.nl")

        invoice2 = self.invoice_1.copy()
        d_date = fields.Date.from_string("2016-07-07")
        old_date = d_date + relativedelta(months=-4, day=1)
        invoice2.date = invoice2.invoice_date = old_date
        invoice2.action_post()

        statement2 = self.env["l10n.nl.vat.statement"].create({"name": "Statement 2"})
        statement2.unreported_move_from_date = False
        statement2.statement_update()
        statement2.with_context(skip_check_config_tag_3b_omzet=True).post()

        self.assertTrue(statement2.unreported_move_ids)
        self.assertEqual(len(statement2.unreported_move_ids), 1)

        self.assertEqual(self.statement_1.btw_total, 21.0)
        self.assertEqual(self.statement_1.format_btw_total, "21.00")

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertTrue(line.is_readonly)

    def test_19_skip_invoice_basis_domain(self):
        self._create_test_invoice()
        self.invoice_1.with_context(skip_invoice_basis_domain=True).action_post()
        self.statement_1.statement_update()
        self.assertEqual(len(self.statement_1.line_ids.ids), 22)

    def test_20_multicompany(self):
        self._create_company_children()

        self.env.user.company_id = self.company_parent
        form = Form(self.env["l10n.nl.vat.statement"])
        statement_parent = form.save()
        self.assertFalse(statement_parent.multicompany_fiscal_unit)
        self.assertTrue(statement_parent.display_multicompany_fiscal_unit)
        self.assertFalse(statement_parent.fiscal_unit_company_ids)
        self.assertFalse(statement_parent.parent_id)

        self.env.user.company_id = self.company_child_1
        form = Form(self.env["l10n.nl.vat.statement"])
        statement_child_1 = form.save()
        self.assertFalse(statement_child_1.multicompany_fiscal_unit)
        self.assertFalse(statement_child_1.display_multicompany_fiscal_unit)
        self.assertFalse(statement_child_1.fiscal_unit_company_ids)
        self.assertFalse(statement_child_1.parent_id)

        self.env.user.company_id = self.company_child_2
        form = Form(self.env["l10n.nl.vat.statement"])
        statement_child_2 = form.save()
        self.assertFalse(statement_child_2.multicompany_fiscal_unit)
        self.assertFalse(statement_child_2.display_multicompany_fiscal_unit)
        self.assertFalse(statement_child_2.fiscal_unit_company_ids)
        self.assertFalse(statement_child_2.parent_id)

        statement_parent.multicompany_fiscal_unit = True
        statement_parent.fiscal_unit_company_ids |= self.company_child_1

        with self.assertRaises(ValidationError):
            statement_parent.fiscal_unit_company_ids |= self.company_child_2

        self.company_child_2.country_id = self.env.ref("base.nl")
        statement_parent.fiscal_unit_company_ids |= self.company_child_2
        statement_child_1._compute_parent_statement_id()
        statement_child_2._compute_parent_statement_id()
        self.assertFalse(statement_parent.parent_id)
        self.assertTrue(statement_child_1.parent_id)
        self.assertTrue(statement_child_2.parent_id)

        statement_child_1.statement_update()
        self.assertFalse(statement_child_1.line_ids)
        statement_child_2.statement_update()
        self.assertFalse(statement_child_1.line_ids)

        company_ids_full_list = statement_parent._get_company_ids_full_list()
        self.assertEqual(len(company_ids_full_list), 3)
