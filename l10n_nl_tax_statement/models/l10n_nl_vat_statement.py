# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang


class VatStatement(models.Model):
    _name = 'l10n.nl.vat.statement'
    _description = 'Netherlands Vat Statement'

    name = fields.Char(
        string='Tax Statement',
        required=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('final', 'Final')],
        readonly=True,
        default='draft',
        copy=False,
        string='Status'
    )
    line_ids = fields.One2many(
        'l10n.nl.vat.statement.line',
        'statement_id',
        'Lines'
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        readonly=True,
        default=lambda self: self.env.user.company_id
    )
    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    date_range_id = fields.Many2one(
        'date.range',
        'Date range',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True
    )
    target_move = fields.Selection([
        ('posted', 'All Posted Entries'),
        ('all', 'All Entries')],
        'Target Moves',
        readonly=True,
        required=True,
        default='posted'
    )
    date_posted = fields.Datetime(readonly=True)
    date_update = fields.Datetime(readonly=True)

    btw_total = fields.Monetary(
        compute='_compute_btw_total',
        string='5g. Total (5c + 5d)'
    )
    format_btw_total = fields.Char(
        compute='_compute_amount_format_btw_total', string='5g - Total'
    )
    move_line_ids = fields.One2many(
        'account.move.line',
        'l10n_nl_vat_statement_id',
        string='Entry Lines',
        readonly=True,
    )
    multicompany_fiscal_unit = fields.Boolean()
    display_multicompany_fiscal_unit = fields.Boolean(
        compute='_compute_display_multicompany_fiscal_unit',
    )
    fiscal_unit_company_ids = fields.Many2many(
        'res.company',
    )
    parent_id = fields.Many2one(
        'l10n.nl.vat.statement',
        'Parent Statement',
        compute='_compute_parent_statement_id',
    )

    def _compute_unreported_move_ids(self):
        for statement in self:
            domain = statement._get_unreported_move_domain()
            move_lines = self.env['account.move.line'].search(domain)
            moves = move_lines.mapped('move_id').sorted('date')
            statement.unreported_move_ids = moves

    @api.depends('company_id')
    def _compute_display_multicompany_fiscal_unit(self):
        for statement in self:
            is_fiscal_entity = True
            child_ids = statement.company_id.child_ids
            if not child_ids:
                is_fiscal_entity = False
            currency = statement.company_id.currency_id
            nl_country = self.env.ref('base.nl')
            if all(c.currency_id != currency for c in child_ids):
                is_fiscal_entity = False
            if all(c.partner_id.country_id != nl_country for c in child_ids):
                is_fiscal_entity = False
            statement.display_multicompany_fiscal_unit = is_fiscal_entity

    @api.depends('company_id', 'from_date', 'to_date')
    def _compute_parent_statement_id(self):
        for statement in self:
            statement.parent_id = False
            if statement.company_id.parent_id:
                parent = self.sudo().search([
                    ('fiscal_unit_company_ids', '=', statement.company_id.id),
                    ('company_id', '!=', statement.company_id.id),
                    ('from_date', '=', statement.from_date),
                    ('to_date', '=', statement.to_date),
                ])
                statement.parent_id = parent

    def _get_unreported_move_domain(self):
        self.ensure_one()
        company_ids = self._get_company_ids_full_list()
        domain = [
            ('company_id', 'in', company_ids),
            ('invoice_id', '!=', False),
            ('l10n_nl_vat_statement_id', '=', False),
        ]
        if self.is_invoice_basis and not self.unreported_move_from_date:
            domain += [
                '|',
                '&',
                ('l10n_nl_date_invoice', '=', False),
                ('date', '<', self.from_date),
                '&',
                ('l10n_nl_date_invoice', '!=', False),
                ('l10n_nl_date_invoice', '<', self.from_date),
            ]
        elif self.is_invoice_basis and self.unreported_move_from_date:
            domain += [
                '|',
                '&', '&',
                ('l10n_nl_date_invoice', '=', False),
                ('date', '<', self.from_date),
                ('date', '>=', self.unreported_move_from_date),
                '&', '&',
                ('l10n_nl_date_invoice', '!=', False),
                ('l10n_nl_date_invoice', '<', self.from_date),
                ('l10n_nl_date_invoice', '>=', self.unreported_move_from_date),
            ]
        else:
            domain += [
                ('date', '<', self.from_date),
            ]
            if self.unreported_move_from_date:
                domain += [
                    ('date', '>=', self.unreported_move_from_date),
                ]
        return domain

    def _get_company_ids_full_list(self):
        self.ensure_one()
        company_ids = [self.company_id.id]
        if self.multicompany_fiscal_unit:
            company_ids += self.fiscal_unit_company_ids.ids
        return company_ids

    unreported_move_ids = fields.One2many(
        'account.move',
        string="Unreported Journal Entries",
        compute='_compute_unreported_move_ids'
    )
    unreported_move_from_date = fields.Date()

    def _compute_is_invoice_basis(self):
        has_invoice_basis = self.env['ir.model.fields'].sudo().search_count([
            ('model', '=', 'res.company'),
            ('name', '=', 'l10n_nl_tax_invoice_basis')
        ])
        for statement in self:
            if has_invoice_basis:
                invoice_basis = statement.company_id.l10n_nl_tax_invoice_basis
                statement.is_invoice_basis = invoice_basis
            else:
                statement.is_invoice_basis = False

    is_invoice_basis = fields.Boolean(
        string='NL Tax Invoice Basis',
        compute='_compute_is_invoice_basis',
    )

    @api.depends('btw_total')
    def _compute_amount_format_btw_total(self):
        for statement in self:
            btw = formatLang(self.env, statement.btw_total, monetary=True)
            statement.format_btw_total = btw

    @api.model
    def _get_unreported_move_from_date(self, from_date):
        """ By default, the unreported date is not set before the start date
        of the earliest report.
        :param from_date: the from_date of the statement to compute the
        unreported date for.
        """
        earliest = self.search([], order='from_date asc', limit=1).from_date
        if not earliest:
            return from_date
        offset_date = from_date + relativedelta(months=-3, day=1)
        return min(from_date, max(earliest, offset_date))

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        company = self.env.user.company_id
        fy_dates = company.compute_fiscalyear_dates(datetime.now())
        defaults.setdefault(
            'from_date',
            datetime.date(fy_dates['date_from'])
            if type(fy_dates['date_from']) != date
            else fy_dates['date_from']
        )
        defaults.setdefault(
            'to_date',
            datetime.date(fy_dates['date_to'])
            if type(fy_dates['date_to']) != date
            else fy_dates['date_to']
        )
        defaults.setdefault('name', company.name)
        defaults.setdefault(
            'unreported_move_from_date',
            self._get_unreported_move_from_date(defaults['from_date']))
        return defaults

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        if self.date_range_id and self.state == 'draft':
            self.update({
                'from_date': self.date_range_id.date_start,
                'to_date': self.date_range_id.date_end,
            })

    @api.onchange('from_date', 'to_date')
    def onchange_date(self):
        display_name = self.company_id.name
        if self.from_date and self.to_date:
            from_date = fields.Date.to_string(self.from_date)
            to_date = fields.Date.to_string(self.to_date)
            display_name += ': ' + ' '.join([from_date, to_date])
        self.name = display_name

    @api.onchange('from_date')
    def onchange_date_from_date(self):
        # by default the unreported_move_from_date is set to
        # a quarter (three months) before the from_date of the statement
        self.unreported_move_from_date = self._get_unreported_move_from_date(
            self.from_date)

    @api.onchange('unreported_move_from_date')
    def onchange_unreported_move_from_date(self):
        self._compute_unreported_move_ids()

    @api.model
    def _get_taxes_domain(self):
        return [('has_moves', '=', True)]

    @api.model
    def _prepare_lines(self):
        lines = {}
        lines['1'] = {
            'code': '1',
            'name': _('Leveringen en/of diensten binnenland')}
        lines['1a'] = {
            'code': '1a', 'omzet': 0.0, 'btw': 0.0,
            'name': _('Leveringen/diensten belast met hoog tarief')}
        lines['1b'] = {
            'code': '1b', 'omzet': 0.0, 'btw': 0.0,
            'name': _('Leveringen/diensten belast met laag tarief')}
        lines['1c'] = {
            'code': '1c', 'omzet': 0.0, 'btw': 0.0,
            'name': _('Leveringen/diensten belast met overige tarieven '
                      'behalve 0%')}
        lines['1d'] = {
            'code': '1d', 'omzet': 0.0, 'btw': 0.0,
            'name': _('1d Prive-gebruik')}
        lines['1e'] = {
            'code': '1e', 'omzet': 0.0,
            'name': _('Leveringen/diensten belast met 0%')}
        lines['2'] = {
            'code': '2',
            'name': _('Verleggingsregelingen: BTW naar u verlegd')}
        lines['2a'] = {
            'code': '2a', 'omzet': 0.0, 'btw': 0.0,
            'name': _('Heffing van omzetbelasting is naar u verlegd')}
        lines['3'] = {
            'code': '3',
            'name': _('Leveringen naar het buitenland')}
        lines['3a'] = {
            'code': '3a', 'omzet': 0.0,
            'name': _('Leveringen naar landen buiten de EU')}
        lines['3b'] = {
            'code': '3b', 'omzet': 0.0,
            'name': _('Leveringen naar landen binnen de EU')}
        lines['3c'] = {
            'code': '3c', 'omzet': 0.0,
            'name': _('Installatie/afstandsverkopen binnen de EU')}
        lines['4'] = {
            'code': '4',
            'name': _('Leveringen vanuit het buitenland')}
        lines['4a'] = {
            'code': '4a', 'omzet': 0.0, 'btw': 0.0,
            'name': _('Verwerving uit landen buiten de EU')}
        lines['4b'] = {
            'code': '4b', 'omzet': 0.0, 'btw': 0.0,
            'name': _('Verwerving van goederen uit landen binnen de EU')}
        lines['5'] = {
            'code': '5',
            'name': _('Voorbelasting')}
        lines['5a'] = {
            'code': '5a', 'btw': 0.0,
            'name': _('Verschuldigde omzetbelasting (rubrieken 1a t/m 4b)')}
        lines['5b'] = {
            'code': '5b', 'btw': 0.0,
            'name': _('Voorbelasting')}
        lines['5c'] = {
            'code': '5c', 'btw': 0.0,
            'name': _('Subtotaal (rubriek 5a min 5b)')}
        lines['5d'] = {
            'code': '5d', 'btw': 0.0,
            'name': _('Vermindering volgens de kleineondernemersregeling')}
        lines['5e'] = {
            'code': '5e', 'btw': 0.0,
            'name': _('Schatting vorige aangifte(n)')}
        lines['5f'] = {
            'code': '5f', 'btw': 0.0,
            'name': _('Schatting deze aangifte')}
        return lines

    @api.model
    def _finalize_lines(self, lines):
        _1ab = lines['1a']['btw']
        _1bb = lines['1b']['btw']
        _1cb = lines['1c']['btw']
        _1db = lines['1d']['btw']
        _2ab = lines['2a']['btw']
        _4ab = lines['4a']['btw']
        _4bb = lines['4b']['btw']

        # 5a is the sum of 1a through 4b
        _5ab = _1ab + _1bb + _1cb + _1db + _2ab + _4ab + _4bb

        # 5b: invert the original sign (5b should be always positive)
        lines['5b']['btw'] = lines['5b']['btw'] * -1
        _5bb = lines['5b']['btw']

        # 5c is the difference: 5a - 5b
        _5cb = _5ab - _5bb

        # update 5a and 5c
        lines['5a'].update({'btw': _5ab})
        lines['5c'].update({'btw': _5cb})

        # omzet (from 1a to 4b): invert the original sign
        # in case it differs from the sign of related btw
        to_be_checked_inverted = ['1a', '1b', '1c', '1d', '2a', '4a', '4b']
        for code in to_be_checked_inverted:
            btw_sign = 1 if lines[code]['btw'] >= 0.0 else -1
            omzet_sign = 1 if lines[code]['omzet'] >= 0.0 else -1
            if btw_sign != omzet_sign:
                lines[code]['omzet'] *= -1

        return lines

    @api.model
    def _get_tags_map(self):
        company_id = self.env.user.company_id.id
        config = self.env['l10n.nl.vat.statement.config'].search([
            ('company_id', '=', company_id)], limit=1
        )
        if not config:
            raise UserError(
                _('Tags mapping not configured for this Company! '
                  'Check the NL BTW Tags Configuration.'))
        return {
            config.tag_1a_omzet.id: ('1a', 'omzet'),
            config.tag_1a_btw.id: ('1a', 'btw'),
            config.tag_1b_omzet.id: ('1b', 'omzet'),
            config.tag_1b_btw.id: ('1b', 'btw'),
            config.tag_1c_omzet.id: ('1c', 'omzet'),
            config.tag_1c_btw.id: ('1c', 'btw'),
            config.tag_1d_omzet.id: ('1d', 'omzet'),
            config.tag_1d_btw.id: ('1d', 'btw'),
            config.tag_1e_omzet.id: ('1e', 'omzet'),
            config.tag_2a_omzet.id: ('2a', 'omzet'),
            config.tag_2a_btw.id: ('2a', 'btw'),
            config.tag_3a_omzet.id: ('3a', 'omzet'),
            config.tag_3b_omzet.id: ('3b', 'omzet'),
            config.tag_3b_omzet_d.id: ('3b', 'omzet'),
            config.tag_3c_omzet.id: ('3c', 'omzet'),
            config.tag_4a_omzet.id: ('4a', 'omzet'),
            config.tag_4a_btw.id: ('4a', 'btw'),
            config.tag_4b_omzet.id: ('4b', 'omzet'),
            config.tag_4b_btw.id: ('4b', 'btw'),
            config.tag_5b_btw.id: ('5b', 'btw'),
        }

    def statement_update(self):
        self.ensure_one()

        if self.state in ['posted', 'final']:
            raise UserError(_('You cannot modify a posted statement!'))

        if self.parent_id:
            return

        # clean old lines
        self.line_ids.unlink()

        # calculate lines
        lines = self._prepare_lines()
        taxes = self._compute_taxes()
        self._set_statement_lines(lines, taxes)
        taxes = self._compute_past_invoices_taxes()
        self._set_statement_lines(lines, taxes)
        self._finalize_lines(lines)

        # create lines
        self.write({
            'line_ids': [(0, 0, line) for line in lines.values()],
            'date_update': fields.Datetime.now(),
        })

    def _compute_past_invoices_taxes(self):
        self.ensure_one()
        company_ids = self._get_company_ids_full_list()
        ctx = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'target_move': self.target_move,
            'company_id': self.company_id.id,
            'fiscal_entities_ids': company_ids,
            'skip_invoice_basis_domain': True,
            'unreported_move': True,
            'is_invoice_basis': self.is_invoice_basis,
            'unreported_move_from_date': self.unreported_move_from_date
        }
        taxes = self.env['account.tax'].with_context(ctx)
        moves_to_include = self.unreported_move_ids.filtered(
            lambda m: m.l10n_nl_vat_statement_include)
        for move_line in moves_to_include.mapped('line_ids'):
            if move_line.tax_exigible:
                if move_line.tax_line_id:
                    taxes |= move_line.tax_line_id
                if move_line.tax_ids:
                    taxes |= move_line.tax_ids
        return taxes

    def _compute_taxes(self):
        self.ensure_one()
        company_ids = self._get_company_ids_full_list()
        ctx = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'target_move': self.target_move,
            'company_id': self.company_id.id,
            'fiscal_entities_ids': company_ids,
        }
        domain = self._get_taxes_domain()
        taxes = self.env['account.tax'].with_context(ctx).search(domain)
        return taxes

    def _set_statement_lines(self, lines, taxes):
        self.ensure_one()
        tags_map = self._get_tags_map()
        for tax in taxes:
            for tag in tax.tag_ids:
                tag_map = tags_map.get(tag.id)
                if tag_map:
                    code, column = tag_map
                    if column == 'omzet':
                        lines[code][column] += tax.base_balance
                    else:
                        lines[code][column] += tax.balance

    def finalize(self):
        self.ensure_one()
        self.write({
            'state': 'final'
        })

    def post(self):
        self.ensure_one()
        prev_open_statements = self.search([
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'draft'),
            ('id', '<', self.id)
        ], limit=1)

        if prev_open_statements:
            raise UserError(
                _('You cannot post a statement if all the previous '
                  'statements are not yet posted! '
                  'Please Post all the other statements first.'))

        self.write({
            'state': 'posted',
            'date_posted': fields.Datetime.now()
        })
        self.unreported_move_ids.filtered(
            lambda m: m.l10n_nl_vat_statement_include
        ).write({
            'l10n_nl_vat_statement_id': self.id,
        })
        company_ids = self._get_company_ids_full_list()
        domain = [
            ('company_id', 'in', company_ids),
            ('l10n_nl_vat_statement_id', '=', False),
        ]
        if self.is_invoice_basis:
            domain += [
                '|',
                '&', '&',
                ('l10n_nl_date_invoice', '=', False),
                ('date', '<=', self.to_date),
                ('date', '>=', self.from_date),
                '&', '&',
                ('l10n_nl_date_invoice', '!=', False),
                ('l10n_nl_date_invoice', '<=', self.to_date),
                ('l10n_nl_date_invoice', '>=', self.from_date),
            ]
        else:
            domain += [
                ('date', '<=', self.to_date),
                ('date', '>=', self.from_date),
            ]
        move_line_ids = self.env['account.move.line'].search(domain)
        updated_move_ids = move_line_ids.mapped('move_id')
        updated_move_ids.write({
            'l10n_nl_vat_statement_id': self.id,
        })

    def reset(self):
        self.write({
            'state': 'draft',
            'date_posted': None
        })
        req = """
            UPDATE account_move_line
            SET l10n_nl_vat_statement_id = NULL
            WHERE
              l10n_nl_vat_statement_id = %s
        """
        self.env.cr.execute(
            req, (self.id, ))

    @api.model
    def _modifiable_values_when_posted(self):
        return ['state']

    def write(self, values):
        for statement in self:
            if statement.state == 'final':
                raise UserError(
                    _('You cannot modify a statement set as final!'))
            if 'state' not in values or values['state'] != 'draft':
                if statement.state == 'posted':
                    for val in values:
                        if val not in self._modifiable_values_when_posted():
                            raise UserError(
                                _('You cannot modify a posted statement! '
                                  'Reset the statement to draft first.'))
        return super().write(values)

    def unlink(self):
        for statement in self:
            if statement.state == 'posted':
                raise UserError(
                    _('You cannot delete a posted statement! '
                      'Reset the statement to draft first.'))
            if statement.state == 'final':
                raise UserError(
                    _('You cannot delete a statement set as final!'))
        super().unlink()

    @api.depends('line_ids.btw')
    def _compute_btw_total(self):
        for statement in self:
            lines = statement.line_ids
            total_lines = lines.filtered(lambda l: l.code in ['5c', '5d'])
            statement.btw_total = sum(line.btw for line in total_lines)

    @api.constrains('fiscal_unit_company_ids')
    def _check_fiscal_unit_company_ids(self):
        for statement in self.sudo():
            unit_companies = statement.fiscal_unit_company_ids
            country_nl = self.env.ref('base.nl')
            if any(u.country_id != country_nl for u in unit_companies):
                raise ValidationError(
                    _('The Companies belonging to a fiscal unit '
                      'must be in The Netherlands.'))
