# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.osv import expression
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang

OMZET_DISPLAY = (
    '1a', '1b', '1c', '1d', '1e',
    '2a',
    '3a', '3b', '3c',
    '4a', '4b'
)

BTW_DISPLAY = (
    '1a', '1b', '1c', '1d',
    '2a',
    '4a', '4b',
    '5a', '5b', '5c', '5d', '5e', '5f'
)

GROUP_DISPLAY = (
    '1', '2', '3', '4', '5'
)

EDITABLE_DISPLAY = (
    '5d', '5e', '5f'
)

TOTAL_DISPLAY = (
    '5a', '5c', '5d', '5e', '5f'
)


class VatStatementLine(models.Model):
    _name = 'l10n.nl.vat.statement.line'
    _description = 'Netherlands Vat Statement Line'
    _order = 'code'

    name = fields.Char()
    code = fields.Char()

    statement_id = fields.Many2one(
        'l10n.nl.vat.statement',
        'Statement'
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='statement_id.company_id.currency_id',
        help='Utility field to express amount currency'
    )
    omzet = fields.Monetary()
    btw = fields.Monetary()
    format_omzet = fields.Char(compute='_compute_amount_format')
    format_btw = fields.Char(compute='_compute_amount_format')

    is_group = fields.Boolean(compute='_compute_is_group')
    is_total = fields.Boolean(compute='_compute_is_group')
    is_readonly = fields.Boolean(compute='_compute_is_readonly')

    @api.depends('omzet', 'btw', 'code')
    def _compute_amount_format(self):
        for line in self:
            omzet = formatLang(self.env, line.omzet, monetary=True)
            btw = formatLang(self.env, line.btw, monetary=True)
            if line.code in OMZET_DISPLAY:
                line.format_omzet = omzet
            if line.code in BTW_DISPLAY:
                line.format_btw = btw

    @api.depends('code')
    def _compute_is_group(self):
        for line in self:
            line.is_group = line.code in GROUP_DISPLAY
            line.is_total = line.code in TOTAL_DISPLAY

    @api.depends('code')
    def _compute_is_readonly(self):
        for line in self:
            if line.statement_id.state == 'draft':
                line.is_readonly = line.code not in EDITABLE_DISPLAY
            else:
                line.is_readonly = True

    def unlink(self):
        for line in self:
            if line.statement_id.state == 'posted':
                raise UserError(
                    _('You cannot delete lines of a posted statement! '
                      'Reset the statement to draft first.'))
            if line.statement_id.state == 'final':
                raise UserError(
                    _('You cannot delete lines of a statement set as final!'))
        super().unlink()

    def view_tax_lines(self):
        self.ensure_one()
        return self.get_lines_action(tax_or_base='tax')

    def view_base_lines(self):
        self.ensure_one()
        return self.get_lines_action(tax_or_base='base')

    def get_lines_action(self, tax_or_base='tax'):
        self.ensure_one()
        action = self.env.ref('account.action_account_moves_all_tree')
        vals = action.read()[0]
        vals['context'] = {}
        vals['domain'] = self._get_move_lines_domain(tax_or_base)
        return vals

    def _get_move_lines_domain(self, tax_or_base):
        statement = self.statement_id
        taxes = self._filter_taxes_by_code(statement._compute_taxes())
        past_taxes = statement._compute_past_invoices_taxes()
        past_taxes = self._filter_taxes_by_code(past_taxes)
        if statement.state == 'draft':
            domain = self._get_domain_draft(taxes, tax_or_base)
            past_domain = self._get_domain_draft(past_taxes, tax_or_base)
        else:
            domain = self._get_domain_posted(taxes, tax_or_base)
            past_domain = self._get_domain_posted(past_taxes, tax_or_base)
        curr_amls = self.env['account.move.line'].search(domain)
        past_amls = self.env['account.move.line'].search(past_domain)
        res = [('id', 'in', past_amls.ids + curr_amls.ids)]
        return res

    def _filter_taxes_by_code(self, taxes):
        self.ensure_one()
        tags_map = self.statement_id._get_tags_map()
        filtered_taxes = self.env['account.tax']
        for tax in taxes:
            for tag in tax.tag_ids:
                tag_map = tags_map.get(tag.id)
                if tag_map and tag_map[0] == self.code:
                    filtered_taxes |= tax
        return filtered_taxes.with_context(taxes.env.context)

    def _get_domain_draft(self, taxes, tax_or_base):
        self.ensure_one()
        ctx = taxes.env.context.copy()
        ctx.update({
            'l10n_nl_statement_tax_ids': taxes.ids
        })
        AccountTax = self.env['account.tax'].with_context(ctx)
        return AccountTax.get_move_lines_domain(tax_or_base=tax_or_base)

    def _get_domain_posted(self, taxes, tax_or_base):
        self.ensure_one()
        statement = self.statement_id
        domain = [('move_id.l10n_nl_vat_statement_id', '=', statement.id)]
        if tax_or_base == 'tax':
            tax_domain = [('tax_line_id', 'in', taxes.ids)]
        else:
            tax_domain = [('tax_ids', 'in', taxes.ids)]
        return expression.AND([domain, tax_domain])
