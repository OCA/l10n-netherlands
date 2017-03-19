# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import Warning as UserError


class VatStatement(models.Model):
    _name = 'l10n.nl.vat.statement'

    name = fields.Char(
        string='Tax Statement',
        required=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted')],
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
        default=lambda self: self.env.user.company_id
    )
    from_date = fields.Date(
        required=True,
    )
    to_date = fields.Date(
        required=True,
    )
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

    @api.model
    def default_get(self, fields_list):
        defaults = super(VatStatement, self).default_get(fields_list)
        company = self.env.user.company_id
        fy_dates = company.compute_fiscalyear_dates(datetime.now())
        from_date = fields.Date.to_string(fy_dates['date_from'])
        to_date = fields.Date.to_string(fy_dates['date_to'])
        defaults.setdefault('from_date', from_date)
        defaults.setdefault('to_date', to_date)
        defaults.setdefault('name', company.name)
        return defaults

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        if self.date_range_id and self.state == 'draft':
            self.write({
                'from_date': self.date_range_id.date_start,
                'to_date': self.date_range_id.date_end,
            })

    @api.model
    def _get_taxes_domain(self):
        return [
            '|', '|',
            ('base_balance', '!=', 0), ('base_balance_regular', '!=', 0),
            '|', '|',
            ('base_balance_refund', '!=', 0), ('balance', '!=', 0),
            '|',
            ('balance_regular', '!=', 0), ('balance_refund', '!=', 0)
        ]

    @api.model
    def _prepare_lines(self):
        lines = {}
        lines['1a'] = {
            'code': '1a', 'omzet': 0.0, 'btw': 0.0,
            'name': _('Leveringen/diensten belast met 21%')}
        lines['1b'] = {
            'code': '1b', 'omzet': 0.0, 'btw': 0.0,
            'name': _('Leveringen/diensten belast met 6%')}
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
        lines['2a'] = {
            'code': '2a', 'omzet': 0.0, 'btw': 0.0,
            'name': _('Heffing van omzetbelasting is naar u verlegd')}
        lines['3a'] = {
            'code': '3a', 'omzet': 0.0,
            'name': _('Leveringen naar landen buiten de EU')}
        lines['3b'] = {
            'code': '3b', 'omzet': 0.0,
            'name': _('Leveringen naar landen binnen de EU')}
        lines['3c'] = {
            'code': '3c', 'omzet': 0.0,
            'name': _('Installatie/afstandsverkopen binnen de EU')}
        lines['4a'] = {
            'code': '4a', 'omzet': 0.0, 'btw': 0.0,
            'name': _('Verwerving uit landen buiten de EU')}
        lines['4b'] = {
            'code': '4b', 'omzet': 0.0, 'btw': 0.0,
            'name': _('Verwerving van goederen uit landen binnen de EU')}
        lines['5a'] = {
            'code': '5a', 'btw': 0.0,
            'name': _('Verschuldigde omzetbelasting (rubrieken 1a t/m 4b)')}
        lines['5b'] = {
            'code': '5b', 'btw': 0.0,
            'name': _('Voorbelasting')}
        lines['5c'] = {
            'code': '5c', 'btw': 0.0,
            'name': _('Subtotaal (rubriek 5a min 5b)')}
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
        _5ab = _1ab + _1bb + _1cb + _1db + _2ab - _4ab - _4bb
        _5bb = lines['5b']['btw']
        _5cb = _5ab - _5bb

        # update 5a and 5c
        lines['5a'].update({'btw': _5ab})
        lines['5c'].update({'btw': _5cb})
        return lines

    @api.model
    def _get_tags_map(self):
        return {
            self.env.ref('l10n_nl.tag_nl_03').id: ('1a', 'omzet'),
            self.env.ref('l10n_nl.tag_nl_20').id: ('1a', 'btw'),
            self.env.ref('l10n_nl.tag_nl_05').id: ('1b', 'omzet'),
            self.env.ref('l10n_nl.tag_nl_22').id: ('1b', 'btw'),
            self.env.ref('l10n_nl.tag_nl_06').id: ('1c', 'omzet'),
            self.env.ref('l10n_nl.tag_nl_23').id: ('1c', 'btw'),
            self.env.ref('l10n_nl.tag_nl_07').id: ('1d', 'omzet'),
            self.env.ref('l10n_nl.tag_nl_24').id: ('1d', 'btw'),
            self.env.ref('l10n_nl.tag_nl_08').id: ('1e', 'omzet'),
            self.env.ref('l10n_nl.tag_nl_10').id: ('2a', 'omzet'),
            self.env.ref('l10n_nl.tag_nl_27').id: ('2a', 'btw'),
            self.env.ref('l10n_nl.tag_nl_12').id: ('3a', 'omzet'),
            self.env.ref('l10n_nl.tag_nl_13').id: ('3b', 'omzet'),
            self.env.ref('l10n_nl.tag_nl_14').id: ('3c', 'omzet'),
            self.env.ref('l10n_nl.tag_nl_16').id: ('4a', 'omzet'),
            self.env.ref('l10n_nl.tag_nl_29').id: ('4a', 'btw'),
            self.env.ref('l10n_nl.tag_nl_17').id: ('4b', 'omzet'),
            self.env.ref('l10n_nl.tag_nl_30').id: ('4b', 'btw'),
            self.env.ref('l10n_nl.tag_nl_33').id: ('5b', 'btw'),
        }

    @api.multi
    def update(self):
        self.ensure_one()

        if self.state == 'posted':
            raise UserError(
                _('You cannot modify a posted statement!'))

        # clean old lines
        self.line_ids.unlink()

        # calculate lines
        lines = self._prepare_lines()
        self._compute_lines(lines)
        self._finalize_lines(lines)

        # create lines
        for line in lines:
            lines[line].update({'statement_id': self.id})
            self.env['l10n.nl.vat.statement.line'].create(
                lines[line]
            )
        self.date_update = fields.Datetime.now()

    def _compute_lines(self, lines):
        ctx = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'target_move': self.target_move,
            'company_id': self.company_id.id,
        }
        tags_map = self._get_tags_map()
        domain = self._get_taxes_domain()
        taxes = self.env['account.tax'].with_context(ctx).search(domain)
        for tax in taxes:
            for tag in tax.tag_ids:
                tag_map = tags_map.get(tag.id)
                if tag_map:
                    column = tag_map[1]
                    code = tag_map[0]
                    if column == 'omzet':
                        lines[code][column] += abs(tax.base_balance)
                    else:
                        lines[code][column] += abs(tax.balance)

    @api.multi
    def post(self):
        self.write({
            'state': 'posted',
            'date_posted': fields.Datetime.now()
        })

    @api.multi
    def reset(self):
        self.write({
            'state': 'draft',
            'date_posted': None
        })

    @api.multi
    def write(self, values):
        for statement in self:
            if 'state' not in values or values['state'] != 'draft':
                if statement.state == 'posted':
                    for val in values:
                        if val != 'state':
                            raise UserError(
                                _('You cannot modify a posted statement! '
                                  'Reset the statement to draft first.'))
        return super(VatStatement, self).write(values)

    @api.multi
    def unlink(self):
        for statement in self:
            if statement.state == 'posted':
                raise UserError(
                    _('You cannot delete a posted statement! '
                      'Reset the statement to draft first.'))
        super(VatStatement, self).unlink()
