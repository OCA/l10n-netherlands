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
from lxml import etree
from datetime import datetime
from openerp import _, models, fields, api, exceptions, release


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

    @api.model
    def default_get(self, fields):
        defaults = super(XafAuditfileExport, self).default_get(fields)
        company = self.env['res.company'].browse([
            self.env['res.company']._company_default_get(
                object=self._model._name)])
        fiscalyear = self.env['account.fiscalyear'].browse([
            self.env['account.fiscalyear'].find(exception=False)])
        if 'company_id' in fields:
            defaults.setdefault('company_id', company.id)
        if 'name' in fields:
            defaults.setdefault(
                'name', _('Auditfile %s %s') % (
                    company.name, datetime.now().strftime('%Y')))
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
        xml = self.env.ref('l10n_nl_xaf_auditfile_export.auditfile_template')\
            .render(values={
                'self': self,
            })
        from_template = etree.fromstring(xml)
        xmldoc = etree.Element(
            from_template.tag,
            nsmap = {
                None: 'http://www.auditfiles.nl/XAF/3.2',
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            })
        xmldoc[:] = from_template[:]
        self.auditfile = base64.b64encode(etree.tostring(
            xmldoc, xml_declaration=True, encoding='utf8'))

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

    @api.multi
    def get_accounts(self):
        '''return browse record list of accounts'''
        return self.env['account.account'].search([])
