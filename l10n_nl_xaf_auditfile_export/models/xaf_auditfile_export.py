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
from StringIO import StringIO
from lxml import etree
from datetime import datetime
from openerp import _, models, fields, api, exceptions, release, modules


MAX_RECORDS = 10000
'''For possibly huge lists, only read chunks from the database in order to
avoid oom exceptions.
This is the default for ir.config_parameter
"l10n_nl_xaf_auditfile_export.max_records"'''


class XafAuditfileExport(models.Model):
    _name = 'xaf.auditfile.export'
    _description = 'XAF auditfile export'
    _inherit = ['mail.thread']
    _order = 'period_start desc'

    @api.depends('name')
    def _auditfile_name_get(self):
        self.auditfile_name = '%s.xaf' % self.name

    name = fields.Char('Name')
    period_start = fields.Many2one(
        'account.period', 'Start period', required=True)
    period_end = fields.Many2one(
        'account.period', 'End period', required=True)
    auditfile = fields.Binary('Auditfile', readonly=True, copy=False)
    auditfile_name = fields.Char(
        'Auditfile filename', compute=_auditfile_name_get)
    date_generated = fields.Datetime(
        'Date generated', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', 'Company', required=True)
    exclude_account_ids = fields.Many2many(
        'account.account',
        string='Accounts to exclude',
        help='''Accounts that should not be shown on the report''')

    @api.model
    def default_get(self, fields):
        defaults = super(XafAuditfileExport, self).default_get(fields)
        company = self.env['res.company'].browse([
            self.env['res.company']._company_default_get(
                object=self._model._name)])
        fiscalyear = self.env['account.fiscalyear'].browse(
            self.env['account.fiscalyear'].find(exception=False) or [])
        if fiscalyear and self.env['account.fiscalyear'].search(
                [('date_start', '<', fiscalyear.date_start)],
                limit=1):
            fiscalyear = self.env['account.fiscalyear'].search(
                [('date_start', '<', fiscalyear.date_start)], limit=1,
                order='date_stop desc')
        if 'company_id' in fields:
            defaults.setdefault('company_id', company.id)
        if 'name' in fields:
            defaults.setdefault(
                'name', _('Auditfile %s %s') % (
                    company.name,
                    fiscalyear.name if fiscalyear
                    else datetime.now().strftime('%Y')))
        if 'period_start' in fields and fiscalyear:
            defaults.setdefault('period_start', fiscalyear.period_ids[0].id)
        if 'period_end' in fields and fiscalyear:
            defaults.setdefault('period_end', fiscalyear.period_ids[-1].id)
        return defaults

    @api.one
    @api.constrains('period_start', 'period_end')
    def check_periods(self):
        if self.period_start.date_start > self.period_end.date_start:
            raise exceptions.ValidationError(
                _('You need to choose consecutive periods!'))

    @api.multi
    def button_generate(self):
        self.date_generated = fields.Datetime.now(self)
        auditfile_template = self._get_auditfile_template()
        xml = auditfile_template.render(values={
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
            self.message_post('\n'.join(map(str, xsd.error_log)))
            return

        self.auditfile = base64.b64encode(etree.tostring(
            xmldoc, xml_declaration=True, encoding='UTF-8'))

    @api.multi
    def _get_auditfile_template(self):
        self.ensure_one()
        return self.env.ref(
            'l10n_nl_xaf_auditfile_export.auditfile_template'
        )

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
                limit=int(self.env['ir.config_parameter'].get_param(
                    'l10n_nl_xaf_auditfile_export.max_records',
                    default=MAX_RECORDS)))
            if not results:
                break
            offset += MAX_RECORDS
            for result in results:
                yield result
            results.env.invalidate_all()
            del results

    @api.multi
    def get_accounts(self):
        '''return browse record list of accounts'''
        return self.env['account.account'].search([
            ('company_id', '=', self.company_id.id),
            ('id', 'not in', self.exclude_account_ids.ids),
        ])

    @api.multi
    def get_periods(self):
        '''return periods in this export'''
        return self.env['account.period'].search([
            ('date_start', '<=', self.period_end.date_stop),
            ('date_stop', '>=', self.period_start.date_start),
            ('company_id', '=', self.company_id.id),
        ])

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
            'select count(id) from account_move_line where period_id in %s '
            'and (company_id=%s or company_id is null) '
            'and account_id not in %s',
            (tuple(p.id for p in self.get_periods()),
                self.company_id.id,
                tuple(self.exclude_account_ids.ids) or (0, )))
        return self.env.cr.fetchall()[0][0] or 0

    @api.multi
    def get_move_line_total_debit(self):
        '''return total debit of move lines'''
        self.env.cr.execute(
            'select sum(debit) from account_move_line where period_id in %s '
            'and (company_id=%s or company_id is null) '
            'and account_id not in %s',
            (tuple(p.id for p in self.get_periods()),
                self.company_id.id,
                tuple(self.exclude_account_ids.ids) or (0, )))
        return self.env.cr.fetchall()[0][0] or 0

    @api.multi
    def get_move_line_total_credit(self):
        '''return total credit of move lines'''
        self.env.cr.execute(
            'select sum(credit) from account_move_line where period_id in %s '
            'and (company_id=%s or company_id is null) '
            'and account_id not in %s',
            (tuple(p.id for p in self.get_periods()),
                self.company_id.id,
                tuple(self.exclude_account_ids.ids) or (0, )))
        return self.env.cr.fetchall()[0][0] or 0

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
        period_ids = [p.id for p in self.get_periods()]
        while True:
            results = self.env['account.move'].search(
                [
                    ('period_id', 'in', period_ids),
                    ('journal_id', '=', journal.id),
                ],
                offset=offset,
                limit=int(self.env['ir.config_parameter'].get_param(
                    'l10n_nl_xaf_auditfile_export.max_records',
                    default=MAX_RECORDS)))
            if not results:
                break
            offset += MAX_RECORDS
            for result in results:
                yield result
            results.env.invalidate_all()
            del results
