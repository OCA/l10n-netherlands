# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.exceptions import UserError


class ReportIntrastat(models.Model):
    """Dutch Intrastat (ICP) report."""
    _name = "l10n_nl.report.intrastat"
    _description = "Declaration of intracommunautary transactions (ICP)"
    _order = "date_to desc"
    _rec_name = 'date_range_id'
    _inherit = ['intrastat.common']

    year_month = fields.Char(
        compute = '_compute_year_month',
        string = 'Period',
        readonly = True,
        help = "Date range of the declaration.")

    last_updated = fields.Datetime(readonly=True, required=False)
    date_range_id = fields.Many2one(
        comodel_name='date.range',
        required=True,
        string='Date range'
    )
    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        string='Company'
    )
    total_amount = fields.Float(
        string='Total amount',
        readonly=True,
        help="Total amount in company currency of the declaration.",
        digits=dp.get_precision('Account'),
    )
    state = fields.Selection(
        string='State',
        selection=[
            ('draft', 'Draft'),
            ('done', 'Done'),
        ],
        default='draft',
        readonly=True,
        help=(
            "State of the declaration. When the state is set to 'Done', "
            "the parameters become read-only."
        ),
    )
    line_ids = fields.One2many(
        string='ICP line',
        comodel_name='l10n_nl.report.intrastat.line',
        inverse_name='report_id',
        readonly=True,
    )

    @api.multi
    @api.depends('date_from', 'date_to')
    def _compute_year_month(self):
        for report in self:
            report.year_month = '-'.join(
            [report.date_from, report.date_to])

    @api.onchange('date_range_id')
    def _onchange_date_range_id(self):
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    @api.multi
    def set_draft(self):
        """ Reset report state to draft. """
        return self.write({'state': 'draft'})

    @api.multi
    def set_done(self):
        """ Validate and close report. """
        return self.write({'state': 'done'})

    @api.multi
    def generate_lines(self):
        """
        Collect the data lines for the given report.
        Unlink any existing lines first.
        """
        self.ensure_one()
        # Other models:
        invoice_model = self.env['account.invoice']
        invoice_line_model = self.env['account.invoice.line']

        # Check whether all configuration done to generate report
        self._check_generate_lines()

        # We need at least these variables to calculate
        if not self.date_from or not self.date_to or not self.company_id:
            return

        # Define search for invoices for period and company:
        company = self.company_id  # simplify access
        invoice_domain = [
            ('type', 'in', ('out_invoice', 'out_refund')),
            ('date_invoice', '>=', self.date_from),
            ('date_invoice', '<=', self.date_to),
            ('state', 'in', ('open', 'paid')),
            ('company_id', '=', company.id),
        ]
        # Search invoices that need intrastat reporting:
        invoice_records = invoice_model.search(
            invoice_domain + [
                ('partner_id.country_id.intrastat', '=', True),
                ('partner_id.country_id.id', '!=', company.country_id.id),
            ]
        )
        invoice_line_records = invoice_line_model.search([
            ('invoice_id', 'in', invoice_records.ids),
            # Ignore invoiceline if taxes should not be included in intrastat
            '|',
            ('invoice_line_tax_ids', '=', False),
            ('invoice_line_tax_ids.exclude_from_intrastat_if_present',
                '!=', 'True')
        ])

        # Gather amounts from invoice lines
        total_amount = 0.0
        partner_amounts_map = {}
        for line in invoice_line_records:
            commercial_partner = \
                line.invoice_id.partner_id.commercial_partner_id
            amounts = partner_amounts_map.setdefault(commercial_partner, {
                'amount_product': 0.0,
                'amount_service': 0.0,
            })
            # Determine product or service, don't look at is_accessory_cost
            if line.product_id.type == 'service':
                amount_type = 'amount_service'
            else:
                amount_type = 'amount_product'
            sign = line.invoice_id.type == 'out_refund' and -1 or 1
            amount = sign * line.price_subtotal
            # Convert currency amount if necessary:
            currency = line.invoice_id.currency_id
            invoice_date = line.invoice_id.date_invoice
            if (currency and currency != company.currency_id):
                amount = currency.with_context(date=invoice_date).compute(
                    amount, company.currency_id, round=True)
            # Accumulate totals:
            amounts[amount_type] += amount  # per partner and type
            total_amount += amount  # grand total

        # Determine new report lines
        new_lines = []
        for (partner, vals) in partner_amounts_map.iteritems():
            if not (vals['amount_service'] or vals['amount_product']):
                continue
            vals.update({'partner_id': partner.id})
            new_lines.append(vals)

        # Set values and replace existing lines by new lines
        self.line_ids.unlink()
        self.write({
            'last_updated': fields.Datetime.now(),
            'line_ids': [(0, False, line) for line in new_lines],
            'total_amount': total_amount
        })

    @api.multi
    def unlink(self):
        """
        Do not allow unlinking of confirmed reports
        """
        if self.filtered(lambda s: s.state != 'draft'):
            raise UserError(_("Cannot remove IPC reports in 'Done' state"))
        return super(ReportIntrastat, self).unlink()


class ReportIntrastatLine(models.Model):
    """Lines for dutch ICP report."""
    _name = "l10n_nl.report.intrastat.line"
    _description = "Declaration of intracommunautary transactions (ICP) line"
    _order = "partner_id, country_code"
    _rec_name = 'partner_id'

    report_id = fields.Many2one(
        string='Report',
        comodel_name='l10n_nl.report.intrastat',
        readonly=True,
        required=True,
        ondelete='cascade'
    )
    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        readonly=True,
        required=True,
    )
    vat = fields.Char(
        string='VAT',
        related='partner_id.vat',
        store=True,
        readonly=True,
    )
    country_code = fields.Char(
        string='Country Code',
        related='partner_id.country_id.code',
        store=True,
        readonly=True,
    )
    amount_product = fields.Float(
        string='Amount products',
        readonly=True,
        digits=dp.get_precision('Account'),
    )
    amount_service = fields.Float(
        string='Amount services',
        readonly=True,
        digits=dp.get_precision('Account'),
    )
