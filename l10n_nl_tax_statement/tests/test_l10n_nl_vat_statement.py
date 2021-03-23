# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime
from dateutil.relativedelta import relativedelta
from mock import patch

import odoo
from odoo import fields
from odoo.tools import convert_file
from odoo.modules.module import get_resource_path
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestVatStatement(TransactionCase):

    def _load(self, module, *args):
        convert_file(
            self.cr,
            'l10n_nl',
            get_resource_path(module, *args),
            {}, 'init', False, 'test', self.registry._assertion_report)

    def setUp(self):
        super().setUp()

        self.Wizard = self.env['l10n.nl.vat.statement.config.wizard']

        self.tag_1 = self.env['account.account.tag'].create({
            'name': 'Tag 1',
            'applicability': 'taxes',
        })
        self.tag_2 = self.env['account.account.tag'].create({
            'name': 'Tag 2',
            'applicability': 'taxes',
        })
        self.tag_3 = self.env['account.account.tag'].create({
            'name': 'Tag 3',
            'applicability': 'taxes',
        })
        self.tag_4 = self.env['account.account.tag'].create({
            'name': 'Tag 4',
            'applicability': 'taxes',
        })

        self.tax_1 = self.env['account.tax'].create({
            'name': 'Tax 1',
            'amount': 21,
            'tag_ids': [(6, 0, [self.tag_1.id])],
        })

        self.tax_2 = self.env['account.tax'].create({
            'name': 'Tax 2',
            'amount': 21,
            'tag_ids': [(6, 0, [self.tag_2.id])],
        })

        self.config = self.env['l10n.nl.vat.statement.config'].create({
            'company_id': self.env.user.company_id.id,
            'tag_1a_omzet': self.tag_1.id,
            'tag_1a_btw': self.tag_2.id,
            'tag_3b_omzet': self.tag_3.id,
            'tag_3b_omzet_d': self.tag_4.id,
        })

        self.statement_1 = self.env['l10n.nl.vat.statement'].create({
            'name': 'Statement 1',
        })

        self.journal_1 = self.env['account.journal'].create({
            'name': 'Journal 1',
            'code': 'Jou1',
            'type': 'sale',
        })

        self.partner = self.env['res.partner'].create({
            'name': 'Test partner'})

        type_account = self.env.ref('account.data_account_type_receivable')

        account_receivable = self.env['account.account'].search([
            ('user_type_id', '=', type_account.id)
        ], order='id asc', limit=1)

        invoice1_vals = [{
            'name': 'Test line',
            'quantity': 1.0,
            'account_id': account_receivable.id,
            'price_unit': 100.0,
            'invoice_line_tax_ids': [(6, 0, [self.tax_1.id])],
        }, {
            'name': 'Test line 2',
            'quantity': 1.0,
            'account_id': account_receivable.id,
            'price_unit': 50.0,
            'invoice_line_tax_ids': [(6, 0, [self.tax_2.id])],
        }]

        self.invoice_1 = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'name': 'ref1',
            'account_id': account_receivable.id,
            'journal_id': self.journal_1.id,
            'date_invoice': fields.Date.today(),
            'type': 'out_invoice',
            'invoice_line_ids': [(0, 0, value) for value in invoice1_vals]
        })

    def test_01_onchange(self):
        """ Unreported move from date is bound by the earliest start date,
        and set to three months earlier otherwise.
        """
        form_0 = Form(self.env['l10n.nl.vat.statement'])
        form_0.from_date = fields.Date.from_string('1975-01-01')
        self.assertEqual(
            form_0.unreported_move_from_date, form_0.from_date)
        form_0.to_date = fields.Date.from_string('1975-12-31')
        statement_0 = form_0.save()

        daterange_type = self.env['date.range.type'].create({
            'name': 'Type 1'
        })
        daterange = self.env['date.range'].create({
            'name': 'Daterange 1',
            'type_id': daterange_type.id,
            'date_start': '2016-01-01',
            'date_end': '2016-12-31',
        })
        form = Form(self.env['l10n.nl.vat.statement'].with_context({
            'active_model': 'l10n.nl.vat.statement',
            'active_ids': [self.statement_1.id],
            'active_id': self.statement_1.id
        }))
        form.date_range_id = daterange
        statement = form.save()
        self.assertEqual(statement.from_date, datetime.date(2016, 1, 1))
        self.assertEqual(statement.to_date, datetime.date(2016, 12, 31))

        check_name = statement.company_id.name
        str_from_date = fields.Date.to_string(statement.from_date)
        str_to_date = fields.Date.to_string(statement.to_date)
        check_name += ': ' + ' '.join([str_from_date, str_to_date])
        self.assertEqual(statement.name, check_name)

        d_from = statement.from_date
        # by default the unreported_move_from_date is set to
        # a quarter (three months) before the from_date of the statement
        new_date = d_from + relativedelta(months=-3, day=1)
        self.assertEqual(statement.unreported_move_from_date, new_date)

        self.assertEqual(statement.btw_total, 0.)

        form.from_date = fields.Date.from_string('1975-02-01')
        self.assertEqual(
            form.unreported_move_from_date, statement_0.from_date)

    def test_02_post_final(self):
        # in draft
        self.assertEqual(self.statement_1.state, 'draft')
        self.statement_1.statement_update()
        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

        # first post
        self.statement_1.statement_update()
        self.statement_1.post()
        self.assertEqual(self.statement_1.state, 'posted')
        self.assertTrue(self.statement_1.date_posted)

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

        # then finalize
        self.statement_1.finalize()
        self.assertEqual(self.statement_1.state, 'final')
        self.assertTrue(self.statement_1.date_posted)

        with self.assertRaises(UserError):
            self.statement_1.write({'name': 'Test Name Modified'})
        with self.assertRaises(UserError):
            self.statement_1.write({'state': 'posted'})
        with self.assertRaises(UserError):
            self.statement_1.write({'date_posted': fields.Datetime.now()})
        with self.assertRaises(UserError):
            self.statement_1.unlink()
        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            with self.assertRaises(UserError):
                line.unlink()

        self.assertEqual(self.statement_1.btw_total, 0.)

    def test_03_reset(self):
        self.statement_1.reset()
        self.assertEqual(self.statement_1.state, 'draft')
        self.assertFalse(self.statement_1.date_posted)

        self.assertEqual(self.statement_1.btw_total, 0.)

        self.statement_1.statement_update()
        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

    def test_04_write(self):
        self.statement_1.post()
        with self.assertRaises(UserError):
            self.statement_1.write({'name': 'Test Name'})

        self.assertEqual(self.statement_1.btw_total, 0.)

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

    def test_08_update_exception2(self):
        self.config.unlink()
        with self.assertRaises(UserError):
            self.statement_1.statement_update()

    def test_09_update_working(self):
        self.invoice_1._onchange_invoice_line_ids()
        self.invoice_1.action_invoice_open()
        self.statement_1.statement_update()
        self.assertEqual(len(self.statement_1.line_ids.ids), 22)

        _1 = self.statement_1.line_ids.filtered(lambda r: r.code == '1')
        _1a = self.statement_1.line_ids.filtered(lambda r: r.code == '1a')

        self.assertEqual(len(_1), 1)
        self.assertEqual(len(_1a), 1)

        self.assertFalse(_1.format_omzet)
        self.assertFalse(_1.format_btw)
        self.assertTrue(_1.is_group)
        self.assertTrue(_1.is_readonly)

        self.assertEqual(_1a.format_omzet, '100.00')
        self.assertEqual(_1a.format_btw, '10.50')
        self.assertFalse(_1a.is_group)
        self.assertTrue(_1a.is_readonly)

        self.assertEqual(self.statement_1.btw_total, 10.5)
        self.assertEqual(self.statement_1.format_btw_total, '10.50')

    def test_10_line_unlink_exception(self):
        self.assertEqual(len(self.statement_1.line_ids.ids), 0)
        self.assertEqual(self.statement_1.btw_total, 0.)

        self.invoice_1.action_invoice_open()
        self.statement_1.statement_update()
        self.statement_1.post()
        with self.assertRaises(UserError):
            self.statement_1.line_ids.unlink()

        self.assertEqual(len(self.statement_1.line_ids.ids), 22)
        self.assertEqual(self.statement_1.btw_total, 10.5)

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertTrue(line.is_readonly)
            with self.assertRaises(UserError):
                line.unlink()

    def test_11_wizard_execute(self):
        wizard = self.Wizard.create({})

        self.assertEqual(wizard.tag_1a_omzet, self.tag_1)
        self.assertEqual(wizard.tag_1a_btw, self.tag_2)

        wizard.write({
            'tag_1a_btw': self.tag_1.id,
            'tag_1a_omzet': self.tag_2.id,
        })

        self.config.unlink()

        wizard_2 = self.Wizard.create({})
        self.assertNotEqual(wizard_2.tag_1a_omzet, self.tag_1)
        self.assertNotEqual(wizard_2.tag_1a_btw, self.tag_2)

        config = self.env['l10n.nl.vat.statement.config'].search(
            [('company_id', '=', self.env.user.company_id.id)],
            limit=1)
        self.assertFalse(config)

        wizard.execute()

        config = self.env['l10n.nl.vat.statement.config'].search(
            [('company_id', '=', self.env.user.company_id.id)],
            limit=1)
        self.assertTrue(config)
        self.assertEqual(config.tag_1a_btw, self.tag_1)
        self.assertEqual(config.tag_1a_omzet, self.tag_2)

        self.assertEqual(self.statement_1.btw_total, 0.)

    def test_12_undeclared_invoice(self):
        self.invoice_1._onchange_invoice_line_ids()
        self.invoice_1.action_invoice_open()
        move = self.invoice_1.move_id.with_context(params={
            'model': 'l10n.nl.vat.statement',
            'id': self.statement_1.id
        })
        move.l10n_nl_add_move_in_statement()
        for line in self.invoice_1.move_id.line_ids:
            self.assertTrue(line.l10n_nl_vat_statement_include)
        move.l10n_nl_unlink_move_from_statement()
        for line in self.invoice_1.move_id.line_ids:
            self.assertFalse(line.l10n_nl_vat_statement_include)

        self.assertEqual(len(self.statement_1.line_ids.ids), 22)

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
        self.statement_1.post()
        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

        invoice2 = self.invoice_1.copy()
        invoice2._onchange_invoice_line_ids()
        invoice2.action_invoice_open()
        statement2 = self.env['l10n.nl.vat.statement'].create({
            'name': 'Statement 2',
        })
        statement2.statement_update()
        statement2.unreported_move_from_date = fields.Date.today()
        statement2.onchange_unreported_move_from_date()
        self.assertFalse(statement2.unreported_move_ids)

        self.assertEqual(self.statement_1.btw_total, 10.5)
        self.assertEqual(self.statement_1.format_btw_total, '10.50')

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertTrue(line.is_readonly)

    def test_13_no_previous_statement_posted(self):
        statement2 = self.env['l10n.nl.vat.statement'].create({
            'name': 'Statement 2',
        })
        statement2.statement_update()
        with self.assertRaises(UserError):
            statement2.post()

        self.assertEqual(self.statement_1.btw_total, 0.)
        self.assertEqual(self.statement_1.format_btw_total, '0.00')

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertFalse(line.is_readonly)

    @odoo.tests.tagged('post_install', '-at_install')
    def test_14_is_invoice_basis(self):
        company = self.statement_1.company_id
        has_invoice_basis = self.env['ir.model.fields'].sudo().search_count([
            ('model', '=', 'res.company'),
            ('name', '=', 'l10n_nl_tax_invoice_basis')
        ])
        if has_invoice_basis:
            company.l10n_nl_tax_invoice_basis = True
            self.statement_1._compute_is_invoice_basis()
            self.assertTrue(self.statement_1.is_invoice_basis)
            company.l10n_nl_tax_invoice_basis = False
            self.statement_1._compute_is_invoice_basis()
            self.assertFalse(self.statement_1.is_invoice_basis)

        self.assertEqual(self.statement_1.btw_total, 0.)
        self.assertEqual(self.statement_1.format_btw_total, '0.00')

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertTrue(line.is_readonly)

    @odoo.tests.tagged('post_install', '-at_install')
    def test_15_invoice_basis_undeclared_invoice(self):
        self.invoice_1._onchange_invoice_line_ids()
        self.invoice_1.action_invoice_open()
        self.statement_1.statement_update()
        self.assertEqual(len(self.statement_1.line_ids.ids), 22)

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

        self.statement_1.with_context(
            skip_check_config_tag_3b_omzet=True
        ).post()
        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

        has_invoice_basis = self.env['ir.model.fields'].sudo().search_count([
            ('model', '=', 'res.company'),
            ('name', '=', 'l10n_nl_tax_invoice_basis')
        ])
        if has_invoice_basis:
            self.statement_1.company_id.l10n_nl_tax_invoice_basis = True
        else:
            self.statement_1.company_id.l10n_nl_tax_invoice_basis = False
        self.statement_1.company_id.country_id = self.env.ref('base.nl')

        invoice2 = self.invoice_1.copy()
        old_date = fields.Date.from_string('2018-12-07')
        invoice2.date_invoice = old_date
        invoice2.action_invoice_open()

        statement2 = self.env['l10n.nl.vat.statement'].create({
            'name': 'Statement 2',
        })
        move_from_date = fields.Date.from_string('2015-07-07')
        statement2.unreported_move_from_date = move_from_date
        statement2.onchange_unreported_move_from_date()
        statement2.unreported_move_ids.l10n_nl_add_move_in_statement()
        statement2.statement_update()
        self.assertTrue(statement2.unreported_move_ids)
        self.assertEqual(len(statement2.unreported_move_ids), 1)

        statement2.with_context(
            skip_check_config_tag_3b_omzet=True
        ).post()

        self.assertEqual(self.statement_1.btw_total, 10.5)
        self.assertEqual(self.statement_1.format_btw_total, '10.50')

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertTrue(line.is_readonly)

    @odoo.tests.tagged('post_install', '-at_install')
    def test_16_is_not_invoice_unreported_move_from_date(self):
        self.invoice_1._onchange_invoice_line_ids()
        self.invoice_1.action_invoice_open()
        self.statement_1.statement_update()
        self.assertEqual(len(self.statement_1.line_ids.ids), 22)
        self.statement_1.is_invoice_basis = False
        self.statement_1.with_context(
            skip_check_config_tag_3b_omzet=True
        ).post()

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())

        self.statement_1.company_id.l10n_nl_tax_invoice_basis = False
        self.statement_1.company_id.country_id = self.env.ref('base.nl')

        invoice2 = self.invoice_1.copy()
        d_date = fields.Date.from_string('2016-07-07')
        old_date = d_date + relativedelta(months=-4, day=1)
        invoice2.date_invoice = old_date
        invoice2.action_invoice_open()

        statement2 = self.env['l10n.nl.vat.statement'].create({
            'name': 'Statement 2',
        })
        move_from_date = fields.Date.from_string('2015-07-07')
        statement2.unreported_move_from_date = move_from_date
        statement2.onchange_unreported_move_from_date()
        statement2.statement_update()
        statement2.with_context(
            skip_check_config_tag_3b_omzet=True
        ).post()

        self.assertTrue(statement2.unreported_move_ids)
        self.assertEqual(len(statement2.unreported_move_ids), 1)

        self.assertEqual(self.statement_1.btw_total, 10.5)
        self.assertEqual(self.statement_1.format_btw_total, '10.50')

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertTrue(line.is_readonly)

    @odoo.tests.tagged('post_install', '-at_install')
    def test_17_is_not_invoice_basis_undeclared_invoice(self):
        self.invoice_1._onchange_invoice_line_ids()
        self.invoice_1.action_invoice_open()
        self.statement_1.statement_update()
        self.assertEqual(len(self.statement_1.line_ids.ids), 22)
        self.statement_1.is_invoice_basis = False
        self.statement_1.with_context(
            skip_check_config_tag_3b_omzet=True
        ).post()

        self.statement_1.company_id.l10n_nl_tax_invoice_basis = False
        self.statement_1.company_id.country_id = self.env.ref('base.nl')

        invoice2 = self.invoice_1.copy()
        d_date = fields.Date.from_string('2016-07-07')
        old_date = d_date + relativedelta(months=-4, day=1)
        invoice2.date_invoice = old_date
        invoice2.action_invoice_open()

        statement2 = self.env['l10n.nl.vat.statement'].create({
            'name': 'Statement 2',
        })
        statement2.unreported_move_from_date = False
        statement2.onchange_unreported_move_from_date()
        statement2.statement_update()
        statement2.with_context(
            skip_check_config_tag_3b_omzet=True
        ).post()

        self.assertTrue(statement2.unreported_move_ids)
        self.assertEqual(len(statement2.unreported_move_ids), 1)

        self.assertEqual(self.statement_1.btw_total, 10.5)
        self.assertEqual(self.statement_1.format_btw_total, '10.50')

        for line in self.statement_1.line_ids:
            self.assertTrue(line.view_base_lines())
            self.assertTrue(line.view_tax_lines())
            self.assertTrue(line.is_readonly)

    def test_18_default_config_l10n_nl_tags(self):
        self._load('l10n_nl', 'data', 'account_account_tag.xml')
        config = self.env['l10n.nl.vat.statement.config'].search([])
        config.unlink()

        path_addon = 'odoo.addons.l10n_nl_tax_statement.'
        path_file = 'wizard.l10n_nl_vat_statement_config_wizard.'
        path_class = 'VatStatementConfigWizard.'
        method = path_addon + path_file + path_class + '_is_l10n_nl_coa'
        with patch(method) as my_mock:
            my_mock.return_value = True

            wizard = self.Wizard.create({})
            self.assertTrue(wizard)

    def test_19_skip_invoice_basis_domain(self):
        self.invoice_1._onchange_invoice_line_ids()
        self.invoice_1.with_context(
            skip_invoice_basis_domain=True
        ).action_invoice_open()
        self.statement_1.statement_update()
        self.assertEqual(len(self.statement_1.line_ids.ids), 22)

    def test_20_multicompany(self):
        company_parent = self.env['res.company'].create({
            'name': 'Parent Company',
            'country_id': self.env.ref('base.nl').id,
        })
        company_child_1 = self.env['res.company'].create({
            'name': 'Child 1 Company',
            'country_id': self.env.ref('base.nl').id,
            'parent_id': company_parent.id,
        })
        company_child_2 = self.env['res.company'].create({
            'name': 'Child 2 Company',
            'country_id': self.env.ref('base.be').id,
            'parent_id': company_parent.id,
        })
        chart_template = self.env.user.company_id.chart_template_id
        self.env.user.company_id = company_parent.id
        chart_template.try_loading_for_current_company()
        form = Form(self.env['l10n.nl.vat.statement'])
        statement_parent = form.save()
        self.assertFalse(statement_parent.multicompany_fiscal_unit)
        self.assertTrue(statement_parent.display_multicompany_fiscal_unit)
        self.assertFalse(statement_parent.fiscal_unit_company_ids)
        self.assertFalse(statement_parent.parent_id)

        self.env.user.company_id = company_child_1.id
        chart_template.try_loading_for_current_company()
        form = Form(self.env['l10n.nl.vat.statement'])
        statement_child_1 = form.save()
        self.assertFalse(statement_child_1.multicompany_fiscal_unit)
        self.assertFalse(statement_child_1.display_multicompany_fiscal_unit)
        self.assertFalse(statement_child_1.fiscal_unit_company_ids)
        self.assertFalse(statement_child_1.parent_id)

        self.env.user.company_id = company_child_2.id
        chart_template.try_loading_for_current_company()
        form = Form(self.env['l10n.nl.vat.statement'])
        statement_child_2 = form.save()
        self.assertFalse(statement_child_2.multicompany_fiscal_unit)
        self.assertFalse(statement_child_2.display_multicompany_fiscal_unit)
        self.assertFalse(statement_child_2.fiscal_unit_company_ids)
        self.assertFalse(statement_child_2.parent_id)

        statement_parent.multicompany_fiscal_unit = True
        statement_parent.fiscal_unit_company_ids |= company_child_1

        with self.assertRaises(ValidationError):
            statement_parent.fiscal_unit_company_ids |= company_child_2

        company_child_2.country_id = self.env.ref('base.nl')
        statement_parent.fiscal_unit_company_ids |= company_child_2
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

    def test_21_defaults_with_fiscalyear(self):
        """
        res.company's compute_fiscalyear_dates() returns date values instead
        of datetime when a fiscal year is present.
        """
        today = fields.Date.context_today(self.env.user)
        date_from = today.replace(month=1, day=1)
        date_to = today.replace(month=12, day=31)
        if not self.env["account.fiscal.year"].search(
                [("date_from", "<=", today),
                 ("date_to", ">=", today),
                 ("company_id", "=", self.env.user.company_id.id)]):
            self.env["account.fiscal.year"].create({
                "name": "This year",
                "date_from": date_from,
                "date_to": date_to,
            })
        form = Form(self.env['l10n.nl.vat.statement'])
        self.assertEqual(
            form.from_date[:10], fields.Date.to_string(date_from))
        self.assertEqual(
            form.to_date[:10], fields.Date.to_string(date_to))
