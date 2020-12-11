# -*- coding: utf-8 -*-
# Copyright (C) 2015 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
from datetime import datetime
import logging
from lxml import etree
import os
import psutil
import shutil
from io import BytesIO
import zipfile
from tempfile import mkdtemp
import time

from openerp import _, models, fields, api, exceptions, release, modules


def chunks(l, n=None):
    """Yield successive n-sized chunks from l."""
    if n is None:
        n = models.PREFETCH_MAX
    for i in range(0, len(l), n):
        yield l[i:i + n]


def memory_info():
    """ Modified from odoo/server/service.py """
    process = psutil.Process(os.getpid())
    pmem = (getattr(process, 'memory_info', None) or process.get_memory_info)()
    return pmem.vms


class XafAuditfileExport(models.Model):
    _name = 'xaf.auditfile.export'
    _description = 'XAF auditfile export'
    _inherit = ['mail.thread']
    _order = 'period_start desc'

    @api.depends('name', 'auditfile')
    def _compute_auditfile_name(self):
        for item in self:
            item.auditfile_name = '%s.xaf' % item.name
            if item.auditfile:
                auditfile = base64.b64decode(item.auditfile)
                zf = BytesIO(auditfile)
                if zipfile.is_zipfile(zf):
                    item.auditfile_name += '.zip'

    name = fields.Char('Name')
    period_start = fields.Many2one(
        'account.period', 'Start period', required=True)
    period_end = fields.Many2one(
        'account.period', 'End period', required=True)
    auditfile = fields.Binary('Auditfile', readonly=True, copy=False)
    auditfile_name = fields.Char(
        'Auditfile filename',
        compute='_compute_auditfile_name',
        store=True
    )
    date_generated = fields.Datetime(
        'Date generated', readonly=True, copy=False)
    data_export = fields.Selection(
        selection=[
            ('default', 'Default'),
            ('all', 'All'),
        ], string='Data record info',
        required=True, default='default',
        help="Select 'All' in order to include "
             "optional partner details and "
             "general account history information "
             "in the exported XAF File. ")
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

    @api.multi
    @api.constrains('period_start', 'period_end')
    def check_periods(self):
        for xaf in self:
            if xaf.period_start.date_start > xaf.period_end.date_start:
                raise exceptions.ValidationError(
                    _('You need to choose consecutive periods!'))

    @api.multi
    def button_generate(self):
        t0 = time.time()
        m0 = memory_info()
        self.date_generated = fields.Datetime.now(self)
        accounts, journals, partner_ids, periods = self._get_data()
        auditfile_template = self._get_auditfile_template()
        xml = auditfile_template.render(values={
            'accounts': accounts,
            'journals': journals,
            'partner_ids': partner_ids,
            'periods': periods,
            'self': self,
        })

        # the following is dealing with the fact that qweb templates don't like
        # namespaces, but we need the correct namespaces for validation
        xml = xml.strip().replace(
            '<auditfile>',
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<auditfile xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns="http://www.auditfiles.nl/XAF/3.2">', 1)

        filename = self.name + '.xaf'
        tmpdir = mkdtemp()
        auditfile = os.path.join(tmpdir, filename)
        archivedir = mkdtemp()
        archive = os.path.join(archivedir, filename)
        try:
            with open(auditfile, 'w+') as tmphandle:
                tmphandle.write(xml)
            del xml

            # Validate the generated XML
            xsd = etree.XMLParser(
                schema=etree.XMLSchema(etree.parse(
                    file(
                        modules.get_module_resource(
                            'l10n_nl_xaf_auditfile_export', 'data',
                            'XmlAuditfileFinancieel3.2.xsd')))))
            etree.parse(auditfile, parser=xsd)
            del xsd

            # Store in compressed format on the auditfile record
            zip_path = shutil.make_archive(
                archive, 'zip', tmpdir, verbose=True)
            with open(zip_path, 'rb') as auditfile_zip:
                self.auditfile = base64.b64encode(auditfile_zip.read())
            logging.getLogger(__name__).info(
                'Created an auditfile in %ss, using %sk memory',
                int(time.time() - t0), (memory_info() - m0) / 1024)

        except etree.XMLSyntaxError as e:
            logging.getLogger(__name__).error(e)
            self.message_post(e)
        finally:
            shutil.rmtree(tmpdir)
            shutil.rmtree(archivedir)

    @api.multi
    def _get_auditfile_template(self):
        self.ensure_one()
        return self.env.ref(
            'l10n_nl_xaf_auditfile_export.xaf_template_%s'
            % self.data_export
        )

    def _get_data(self):
        periods = self.env['account.period'].search([
            ('date_start', '<=', self.period_end.date_stop),
            ('date_stop', '>=', self.period_start.date_start),
            ('company_id', '=', self.company_id.id),
        ], order='date_start, special desc')

        self._cr.execute(
            "SELECT partner_id, account_id, journal_id "
            "FROM account_move_line "
            "WHERE period_id IN %s AND account_id NOT IN %s "
            "AND company_id=%s ",
            (tuple(periods._ids),
             tuple(self.exclude_account_ids._ids or [0]),
             self.company_id.id))
        res = self._cr.fetchall()

        partner_ids = list(set([x[0] for x in res]))

        account_ids = list(set([x[1] for x in res]))
        accounts = self.env['account.account'].search([
            ('id', 'in', account_ids)], order='code')

        journal_ids = list(set([x[2] for x in res]))
        journals = self.env['account.journal'].search([
            ('id', 'in', journal_ids)], order='code')

        return accounts, journals, partner_ids, periods

    @api.multi
    def get_odoo_version(self):
        '''return odoo version'''
        return release.version

    @api.multi
    def get_partners(self, partner_ids):
        '''return a generator over partners'''
        for chunk in chunks(partner_ids):
            for partner in self.env['res.partner'].browse(chunk):
                yield partner
            self.env.invalidate_all()

    @api.multi
    def get_move_line_count(self, periods):
        '''return amount of move lines'''
        self.env.cr.execute(
            'select count(id) from account_move_line where period_id in %s '
            'and (company_id=%s or company_id is null) '
            'and account_id not in %s',
            (tuple(p.id for p in periods),
                self.company_id.id,
                tuple(self.exclude_account_ids.ids) or (0, )))
        return self.env.cr.fetchall()[0][0] or 0

    @api.multi
    def get_move_line_total_debit(self, periods):
        '''return total debit of move lines'''
        self.env.cr.execute(
            'select sum(debit) from account_move_line where period_id in %s '
            'and (company_id=%s or company_id is null) '
            'and account_id not in %s',
            (tuple(p.id for p in periods),
                self.company_id.id,
                tuple(self.exclude_account_ids.ids) or (0, )))
        return self.env.cr.fetchall()[0][0] or 0

    @api.multi
    def get_move_line_total_credit(self, periods):
        '''return total credit of move lines'''
        self.env.cr.execute(
            'select sum(credit) from account_move_line where period_id in %s '
            'and (company_id=%s or company_id is null) '
            'and account_id not in %s',
            (tuple(p.id for p in periods),
                self.company_id.id,
                tuple(self.exclude_account_ids.ids) or (0, )))
        return self.env.cr.fetchall()[0][0] or 0

    @api.multi
    def get_moves(self, journal, periods):
        '''return moves for a journal, generator style'''
        move_ids = self.env['account.move'].search([
            ('period_id', 'in', periods.ids),
            ('journal_id', '=', journal.id)]).ids
        self.env.invalidate_all()
        for chunk in chunks(move_ids):
            for move in self.env['account.move'].browse(chunk):
                yield move
            self.env.invalidate_all()
