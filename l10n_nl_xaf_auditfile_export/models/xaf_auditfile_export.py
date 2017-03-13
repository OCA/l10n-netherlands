# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import base64
import collections
from StringIO import StringIO
from lxml import etree
from datetime import datetime, timedelta
from dateutil.rrule import rrule, MONTHLY
from odoo import _, models, fields, api, exceptions, release, modules


MAX_RECORDS = 10000
'''For possibly huge lists, only read chunks from the database in order to
avoid oom exceptions.
This is the default for ir.config_parameter
"l10n_nl_xaf_auditfile_export.max_records"'''


class XafAuditfileExport(models.Model):
    _name = 'xaf.auditfile.export'
    _description = 'XAF auditfile export'
    _inherit = ['mail.thread']
    _order = 'date_start desc'

    @api.depends('name')
    def _auditfile_name_get(self):
        self.auditfile_name = '%s.xaf' % self.name

    @api.multi
    def _compute_fiscalyear_name(self):
        for auditfile in self:
            if auditfile.date_start:
                auditfile.fiscalyear_name = auditfile.date_start[0:4]

    name = fields.Char('Name')
    date_start = fields.Date('Start date', required=True)
    date_end = fields.Date('End date', required=True)
    fiscalyear_name = fields.Char(compute='_compute_fiscalyear_name')
    auditfile = fields.Binary('Auditfile', readonly=True, copy=False)
    auditfile_name = fields.Char(
        'Auditfile filename', compute=_auditfile_name_get)
    date_generated = fields.Datetime(
        'Date generated', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', 'Company', required=True)

    @api.model
    def default_get(self, fields_list):
        defaults = super(XafAuditfileExport, self).default_get(fields_list)
        company = self.env.user.company_id
        fy_dates = company.compute_fiscalyear_dates(datetime.now())
        date_from = fields.Date.to_string(fy_dates['date_from'])
        date_to = fields.Date.to_string(fy_dates['date_to'])
        defaults.setdefault('date_start', date_from)
        defaults.setdefault('date_end', date_to)
        if 'company_id' in fields_list:
            defaults.setdefault('company_id', company.id)
        if 'name' in fields_list:
            defaults.setdefault(
                'name', _('Auditfile %s %s') % (
                    company.name,
                    datetime.now().strftime('%Y')))

        return defaults

    @api.one
    @api.constrains('date_start', 'date_end')
    def check_dates(self):
        if self.date_start >= self.date_end:
            raise exceptions.ValidationError(
                _('Starting date must be anterior ending date!'))

    @api.multi
    def button_generate(self):
        self.date_generated = fields.Datetime.now(self)
        xml = self.env.ref('l10n_nl_xaf_auditfile_export.auditfile_template')\
            .render(values={
                'self': self,
            })
        # the following is dealing with the fact that qweb templates don't like
        # namespaces, but we need the correct namespaces for validation
        # we inject them at parse time in order not to traverse the document
        # multiple times
        default_namespace = 'http://www.auditfiles.nl/XAF/3.2'
        iterparse = etree.iterparse(
            StringIO(xml),
            remove_blank_text=True, remove_comments=True)
        for action, element in iterparse:
            element.tag = '{%s}%s' % (default_namespace, element.tag)
        del xml
        xmldoc = etree.Element(
            iterparse.root.tag,
            nsmap={
                None: default_namespace,
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            })
        for element in iterparse.root:
            xmldoc.append(element)
        del iterparse

        xsd = etree.XMLSchema(
            etree.parse(
                file(
                    modules.get_module_resource(
                        'l10n_nl_xaf_auditfile_export', 'data',
                        'XmlAuditfileFinancieel3.2.xsd'))))
        if not xsd.validate(xmldoc):
            self.message_post('<br><br>\n'.join(map(str, xsd.error_log)))
            return

        self.auditfile = base64.b64encode(etree.tostring(
            xmldoc, xml_declaration=True, encoding='UTF-8'))

    @api.multi
    def get_odoo_version(self):
        '''return odoo version'''
        return release.version

    @api.multi
    def get_partners(self):
        '''return a generator over partners and suppliers'''
        offset = 0
        while True:
            results = self.env['res.partner'].search(
                [
                    '|',
                    ('customer', '=', True),
                    ('supplier', '=', True),
                    '|',
                    ('company_id', '=', False),
                    ('company_id', '=', self.company_id.id),
                ],
                offset=offset,
                limit=self.env['ir.config_parameter'].get_param(
                    'l10n_nl_xaf_auditfile_export.max_records',
                    default=MAX_RECORDS))
            if not results:
                break
            offset += MAX_RECORDS
            for result in results:
                yield result
            results.env.invalidate_all()
            del results

    @api.multi
    def get_accounts(self):
        '''return recordset of accounts'''
        return self.env['account.account'].search([
            ('company_id', '=', self.company_id.id),
        ])

    @api.model
    def get_period_number(self, date):
        period_id = date[3:4] + date[5:7]
        return period_id

    @api.multi
    def get_periods(self):

        def month_end_date(date_start):
            month = date_start.month
            year = date_start.year
            month += 1
            if month == 13:
                month = 1
                year += 1

            start_date_next_month = date_start.replace(month=month, year=year)
            return start_date_next_month - timedelta(days=1)

        self.ensure_one()
        months = rrule(
            freq=MONTHLY, bymonth=(),
            dtstart=fields.Date.from_string(self.date_start),
            until=fields.Date.from_string(self.date_end)
        )

        Period = collections.namedtuple(
            'Period',
            'number name date_start date_end'
        )
        periods = []
        for dt_start in list(months):
            date_start = fields.Date.to_string(dt_start.date())
            date_end = fields.Date.to_string(month_end_date(dt_start.date()))
            periods.append(Period(
                number=self.get_period_number(date_start),
                name=dt_start.strftime('%B') + ' ' + self.fiscalyear_name,
                date_start=date_start,
                date_end=date_end,
            ))

        return periods

    @api.multi
    def get_taxes(self):
        '''return taxes'''
        return self.env['account.tax'].search([
            ('company_id', '=', self.company_id.id),
        ])

    @api.multi
    def get_move_line_count(self):
        '''return amount of move lines'''
        self.env.cr.execute(
            'select count(*) from account_move_line '
            'where date >= \'' + self.date_start + '\' '
            'and date <= \'' + self.date_end + '\' '
            'and (company_id=%s or company_id is null)',
            (self.company_id.id, ))
        return self.env.cr.fetchall()[0][0]

    @api.multi
    def get_move_line_total_debit(self):
        '''return total debit of move lines'''
        self.env.cr.execute(
            'select sum(debit) from account_move_line '
            'where date >= \'' + self.date_start + '\' '
            'and date <= \'' + self.date_end + '\' '
            'and (company_id=%s or company_id is null)',
            (self.company_id.id, ))
        return self.env.cr.fetchall()[0][0]

    @api.multi
    def get_move_line_total_credit(self):
        '''return total credit of move lines'''
        self.env.cr.execute(
            'select sum(credit) from account_move_line '
            'where date >= \'' + self.date_start + '\' '
            'and date <= \'' + self.date_end + '\' '
            'and (company_id=%s or company_id is null)',
            (self.company_id.id, ))
        return self.env.cr.fetchall()[0][0]

    @api.multi
    def get_journals(self):
        '''return journals'''
        return self.env['account.journal'].search([
            ('company_id', '=', self.company_id.id),
        ])

    @api.multi
    def get_moves(self, journal):
        '''return moves for a journal, generator style'''
        offset = 0
        while True:
            results = self.env['account.move'].search(
                [
                    ('date', '>=', self.date_start),
                    ('date', '<=', self.date_end),
                    ('journal_id', '=', journal.id),
                ],
                offset=offset,
                limit=self.env['ir.config_parameter'].get_param(
                    'l10n_nl_xaf_auditfile_export.max_records',
                    default=MAX_RECORDS))
            if not results:
                break
            offset += MAX_RECORDS
            for result in results:
                yield result
            results.env.invalidate_all()
            del results

    @api.model
    def get_move_period_number(self, move):
        period_number = self.get_period_number(move.date)
        return period_number
