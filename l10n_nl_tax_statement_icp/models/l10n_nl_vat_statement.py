# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VatStatement(models.Model):
    _inherit = 'l10n.nl.vat.statement'

    tag_3b_omzet = fields.Many2one(
        'account.account.tag',
        compute='_compute_tag_3b_omzet'
    )
    tag_3b_omzet_d = fields.Many2one(
        'account.account.tag',
        compute='_compute_tag_3b_omzet'
    )
    icp_line_ids = fields.One2many(
        'l10n.nl.vat.statement.icp.line',
        'statement_id',
        string='ICP Lines',
        readonly=True
    )
    icp_total = fields.Monetary(
        string='Total ICP amount',
        readonly=True,
        help='Total amount in currency of the statement.'
    )

    @api.depends('company_id')
    def _compute_tag_3b_omzet(self):
        ''' Computes Tag 3b omzet'''
        for statement in self:
            config = self.env['l10n.nl.vat.statement.config'].search([
                ('company_id', '=', statement.company_id.id)
            ], limit=1)
            statement.tag_3b_omzet = config.tag_3b_omzet
            statement.tag_3b_omzet_d = config.tag_3b_omzet_d

    def _compute_icp_lines(self):
        ''' Computes ICP lines for the report'''
        IcpLine = self.env['l10n.nl.vat.statement.icp.line']
        for statement in self:
            statement.icp_line_ids.unlink()
            statement.icp_total = 0.0
            amounts_map = statement._get_partner_amounts_map()
            for partner_id in amounts_map:
                icp_values = self._prepare_icp_line(amounts_map[partner_id])
                icp_values['partner_id'] = partner_id
                icp_values['statement_id'] = statement.id
                newline = IcpLine.create(icp_values)
                icp_total = newline.amount_products + newline.amount_services
                statement.icp_total += icp_total

    @api.model
    def _prepare_icp_line(self, partner_amounts):
        ''' Prepares an internal data structure representing the ICP line'''
        return {
            'country_code': partner_amounts['country_code'],
            'vat': partner_amounts['vat'],
            'amount_products': partner_amounts['amount_products'],
            'amount_services': partner_amounts['amount_services'],
            'currency_id': partner_amounts['currency_id'],
        }

    def _is_3b_omzet_line(self, line):
        self.ensure_one()

        tag_3b_omzet = self.tag_3b_omzet
        tags = line.tax_ids.mapped('tag_ids')
        if any(tags.filtered(lambda r: r == tag_3b_omzet)):
            return True
        return False

    def _is_3b_omzet_diensten_line(self, line):
        self.ensure_one()

        tag_3b_omzet_d = self.tag_3b_omzet_d
        tags = line.tax_ids.mapped('tag_ids')
        if any(tags.filtered(lambda r: r == tag_3b_omzet_d)):
            return True
        return False

    def _get_partner_amounts_map(self):
        ''' Generate an internal data structure representing the ICP line'''
        self.ensure_one()

        partner_amounts_map = {}
        for line in self.move_line_ids:
            is_3b_omzet = self._is_3b_omzet_line(line)
            is_3b_omzet_diensten = self._is_3b_omzet_diensten_line(line)
            if is_3b_omzet or is_3b_omzet_diensten:
                vals = self._prepare_icp_line_from_move_line(line)
                if vals['partner_id'] not in partner_amounts_map:
                    self._init_partner_amounts_map(partner_amounts_map, vals)
                self._update_partner_amounts_map(partner_amounts_map, vals)
        return partner_amounts_map

    def _check_config_tag_3b_omzet(self):
        ''' Checks the tag 3b Omzet, as configured for the BTW statement'''
        if self.env.context.get('skip_check_config_tag_3b_omzet'):
            return
        for statement in self:
            if not statement.tag_3b_omzet or not statement.tag_3b_omzet_d:
                raise UserError(
                    _('Tag 3b omzet not configured for this Company! '
                      'Check the NL BTW Tags Configuration.'))

    @classmethod
    def _update_partner_amounts_map(cls, partner_amounts_map, vals):
        ''' Update amounts of the internal ICP lines data structure'''
        map_data = partner_amounts_map[vals['partner_id']]
        map_data['amount_products'] += vals['amount_products']
        map_data['amount_services'] += vals['amount_services']

    @classmethod
    def _init_partner_amounts_map(cls, partner_amounts_map, vals):
        ''' Initialize the internal ICP lines data structure'''
        partner_amounts_map[vals['partner_id']] = {
            'country_code': vals['country_code'],
            'vat': vals['vat'],
            'currency_id': vals['currency_id'],
            'amount_products': 0.0,
            'amount_services': 0.0,
        }

    def _prepare_icp_line_from_move_line(self, line):
        ''' Gets move line details and prepares ICP report line data'''
        self.ensure_one()

        balance = line.balance and -line.balance or 0
        if line.company_currency_id != self.currency_id:
            balance = line.company_currency_id.with_context(
                date=line.date
            ).compute(balance, self.currency_id, round=True)
        if self.env["ir.config_parameter"].sudo().get_param(
                "l10n_nl_tax_statement_icp.icp_amount_by_tag_or_product",
                "tag") == "product":
            is_service = not line.product_id or (
                line.product_id.type == "service")
        else:
            is_service = self._is_3b_omzet_diensten_line(line)
        amount_products = balance
        amount_services = 0.0
        if is_service:
            amount_products = 0.0
            amount_services = balance

        return {
            'partner_id': line.partner_id.id,
            'country_code': line.partner_id.country_id.code,
            'vat': line.partner_id.vat,
            'amount_products': amount_products,
            'amount_services': amount_services,
            'currency_id': self.currency_id.id,
        }

    def reset(self):
        ''' Removes ICP lines if reset to draft'''
        self.mapped('icp_line_ids').unlink()
        return super().reset()

    def post(self):
        ''' Checks configuration when validating the statement'''
        self.ensure_one()
        self._check_config_tag_3b_omzet()
        res = super().post()
        self._compute_icp_lines()
        return res

    @api.model
    def _modifiable_values_when_posted(self):
        ''' Returns the modifiable fields even when the statement is posted'''
        res = super()._modifiable_values_when_posted()
        res.append('icp_line_ids')
        res.append('icp_total')
        return res

    def icp_update(self):
        ''' Update button'''
        self.ensure_one()

        if self.state in ['final']:
            raise UserError(
                _('You cannot modify a final statement!'))

        # clean old lines
        self.icp_line_ids.unlink()

        # check config
        self._check_config_tag_3b_omzet()

        # create lines
        self._compute_icp_lines()
