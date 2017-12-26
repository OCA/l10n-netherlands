# -*- coding: utf-8 -*-
# Copyright 2015-2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import logging
import os
from datetime import datetime
from lxml import etree

from openerp import _, api, fields, models, modules
from openerp.exceptions import ValidationError
from openerp.sql_db import dsn
from openerp.tools.config import config

from ..auditfile import create_auditfile


_logger = logging.getLogger(__name__)


def get_filetype_dir(filetype):
    """Each functional type of file will have its own main directory."""
    # This function might be made part of a general module
    # in the knowledge repository
    d = os.path.join(config['data_dir'], 'file_cabinet', filetype)
    if not os.path.exists(d):
        os.makedirs(d, 0700)
    return d


def get_auditfile_path(filename):
    return os.path.join(get_filetype_dir('auditfile'), filename)


class XafAuditfileExport(models.Model):
    _name = 'xaf.auditfile.export'
    _description = 'XAF auditfile export'
    _inherit = ['mail.thread']
    _order = 'period_start desc'

    name = fields.Char('Name')
    period_start = fields.Many2one(
        'account.period', 'Start period', required=True)
    period_end = fields.Many2one(
        'account.period', 'End period', required=True)
    auditfile_url = fields.Char(
        'Auditfile url', readonly=True, copy=False)
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

    @api.onchange('company_id')
    def _onchange_company_id(self):
        company = self.company_id
        if not company:
            self.period_start = False
            self.period_end = False
        else:
            if company != self.period_start.company_id or \
                    company != self.period_end.company_id:
                fiscalyear_model = self.env['account.fiscalyear'].with_context(
                    company_id=company.id)
                fiscalyear_id = fiscalyear_model.find(exception=False)
                if not fiscalyear_id:
                    self.period_start = False
                    self.period_end = False
                else:
                    fiscalyear = fiscalyear_model.browse([fiscalyear_id])
                    # New check for company, maybe only one was wrong
                    if company != self.period_start.company_id:
                        self.period_start = fiscalyear.period_ids[0]
                    if company != self.period_end.company_id:
                        self.period_end = fiscalyear.period_ids[-1]
        # If company.id == False, will disable selecting period,
        # else period has to be for the right company
        domain = {}
        company_domain = [('company_id', '=', company.id)]
        domain['period_start'] = company_domain
        domain['period_end'] = company_domain
        return {'domain': domain}

    @api.one
    @api.constrains('period_start', 'period_end')
    def check_periods(self):
        if self.period_start.date_start > self.period_end.date_start:
            raise ValidationError(
                _('You need to choose consecutive periods!'))

    @api.multi
    def button_generate(self):
        self.date_generated = fields.Datetime.now(self)
        # Check wether we can create validation schema
        xsd_path = modules.get_module_resource(
            'l10n_nl_xaf_auditfile_export', 'data',
            'XmlAuditfileFinancieel3.2.xsd')
        xsd = xsd = etree.XMLSchema(etree.parse(xsd_path))
        #  Collect input specification
        specification = {
            'company_id': self.company_id.id,
            'date_start': self.period_start.date_start,
            'date_stop': self.period_end.date_stop}
        # Determine path for auditfile
        auditfile_name = '%s.xaf' % self.name.replace(' ', '_')
        auditfile_path = get_auditfile_path(auditfile_name)
        # Compose connection string to odoo DB-name
        db, connection_string = dsn(self.env.cr.dbname)
        # Now ready to call function to create xml file
        _logger.debug(_("Start creation of xml audit file"))
        create_auditfile(specification, auditfile_path, connection_string)
        _logger.debug(_(
            "Before parsing created xml audit file %s") % auditfile_path)
        parser = etree.iterparse(auditfile_path, schema=xsd)
        try:
            for action, element in parser:
                # We come here at the end of each element
                element.clear()
        except etree.XMLSyntaxError as e:
            self.message_post('Invalid audit file:\n%s' % e)
            return
        self.auditfile_url = (
            '/file_cabinet/auditfile?filename=%s' % auditfile_name)
        _logger.debug(_("Completed processing of audit file"))
