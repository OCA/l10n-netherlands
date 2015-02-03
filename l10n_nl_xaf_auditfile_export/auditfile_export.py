# -*- encoding: utf-8 -*-
##############################################################################
#
#    XAF Auditfile export
#    Copyright (C) 2014 ONESTEiN BV (<http://www.onestein.nl>).
#    Copyright (C) 2012-2013 Neobis ICT Dienstverlening BV
#    <http://www.neobis.nl>
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


from openerp.osv import fields, orm
from openerp.tools.translate import _
from lxml import etree
import sys
from openerp import release
import datetime
import time
import logging
from openerp.modules import get_module_resource
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class auditfile_generate(orm.Model):
    """
    auditfile_export module exports all financial data in xml format
    """

    _logger = logging.getLogger('auditfile_generate')

    _name = "auditfile.generate"
    _description = "Auditfile_export generation"

    def _check_state(self, cr, uid, ids, state, args, context=None):
        res = {}
        for rec_id in ids:
            exists_attachment = self.pool.get('ir.attachment').search(
                cr, uid, ['&', ('res_id', '=', rec_id), ('res_model', '=', 'auditfile.generate')], context=context
            )
            if exists_attachment:
                res[rec_id] = 'done'
            else:
                res[rec_id] = 'ready'
        return res

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'template_content': fields.text('Template', required=True),
        'period_start': fields.many2one('account.period', 'Start Period', required=True),
        'period_stop': fields.many2one('account.period', 'Stop Period', required=True),
        'state': fields.function(
            _check_state, string="Status", type='selection',
            selection=[('ready', 'Ready'), ('done', 'Printed')], readonly=True, store=False
        ),
        'date_printed': fields.datetime("Date Printed", readyonly=True, select="0"),
        'notes': fields.text('Notes'),
    }

    # dates validation
    def _check_dates(self, cr, uid, ids, context=None):
        for export in self.browse(cr, uid, ids, context=context):
            if export.period_start.date_start > export.period_stop.date_stop:
                return False
        return True

    # template (default)
    def _default_template(self, cr, uid, ids):
        self._logger.info('search for built-in xml_template')

        _file = get_module_resource(
            'l10n_nl_xaf_auditfile_export', 'data', 'auditfile_template.xml')
        if not _file:
            raise Warning(_('Data Error'), _('Invalid built-in template'))

        return open(_file).read()

    _defaults = {
        'template_content': _default_template,
        'name': lambda self, cr, uid, context={}: 'auditfile %s' % fields.date.context_today(self, cr, uid, context=context),
        'period_start': 1,
        'period_stop': 12,
    }

    _constraints = [(_check_dates, _('Please, check periods'),
                    ['period_start', 'period_stop'])]

    # creates auditfile
    def create_auditfile(self, cr, uid, ids, context=None):
        self._logger.info('create auditfile')
        mod_obj = self.pool.get('ir.model.data')

        _date_format = DEFAULT_SERVER_DATE_FORMAT
        _output_file = '.xaf'

        data = self.browse(cr, uid, ids[0], context=context)

        # partners search
        partners_obj = self.pool.get("res.partner")
        partners_obj_ids = partners_obj.search(
            cr, uid, ['|', ('supplier', '=', 'True'), ('customer', '=', 'True')], context=context
        )
        partners = partners_obj.browse(cr, uid, partners_obj_ids, context=context)

        if not partners:
            raise Warning(_('Data Error'), _('There are no partners to export'))

        def _validate_country_ids(partners):
            names = []
            if not partners[0].company_id.country_id:
                names.append(partners[0].company_id.name)
            for partner in partners:
                if not partner.country_id:
                    names.append(partner.name)
                    break
            if names:
                raise Warning(
                    _('Data Error'), _('Following partners have no country code: %s')
                    % (', '.join(names))
                )
            return True
        _validate_country_ids(partners)

        # periods search
        period_obj = self.pool.get("account.period")
        period_ids = period_obj.search(
            cr, uid, ['&', ('id', '>=', data.period_start.id), ('id', '<=', data.period_stop.id)], context=context
        )
        periods = period_obj.browse(cr, uid, period_ids, context=context)

        # journal search
        journal_obj = self.pool.get("account.journal")
        journal_ids = journal_obj.search(cr, uid, [], context=context)
        journals = journal_obj.browse(cr, uid, journal_ids, context=context)

        # accounts search
        account_obj = self.pool.get("account.account")
        account_ids = account_obj.search(cr, uid, [], context=context)
        accounts = account_obj.browse(cr, uid, account_ids, context=context)

        user_type_id = mod_obj.get_object_reference(cr, uid, 'account', 'data_account_type_view')[1]
        coa_ids = account_obj.search(cr, uid, ['&', ('user_type', '=', user_type_id), ('parent_id', '=', False)], context=context)
        coa = account_obj.browse(cr, uid, coa_ids[0], context=context)

        # tax code search
        tax_code_obj = self.pool.get("account.tax.code")
        tax_code_ids = tax_code_obj.search(cr, uid, [], context=context)
        tax_codes_list = tax_code_obj.browse(cr, uid, tax_code_ids, context=context)

        # tax search
        tax_obj = self.pool.get("account.tax")
        tax_ids = tax_obj.search(cr, uid, [
            ('tax_code_id', 'in', tax_code_ids)], context=context)
        tax_codes = set(t.tax_code_id for t in tax_obj.browse(cr, uid, tax_ids, context=context))

        def _validate_tax_code_ids(tax_codes):
            names = []
            for tax_code in tax_codes:
                if not tax_code.code:
                    names.append(tax_code.name)
            if names:
                raise Warning(
                    _('Data Error'), _('Following taxes have no tax code: %s')
                    % (', '.join(names))
                )
            return True

        _validate_tax_code_ids(tax_codes)

        # moves search
        move_obj = self.pool.get("account.move")

        journals_moves = {}
        for journal in journals:
            move_ids = move_obj.search(
                cr, uid, ['&', ("journal_id", "=", journal.id), ("period_id", "in", period_ids)], context=context
            )
            journals_moves[journal.id] = move_obj.browse(cr, uid, move_ids, context=context)

        # define fiscal year by start period
        fiscal_year = datetime.datetime.strptime(periods[0].date_start, _date_format).year

        # lambda functions
        custSupTp = lambda s, c: 'B' if s and c \
            else 'S' if s else 'C' if c else 'O'
        accTp = lambda t: 'B' if t == 'income' or t == 'expense' \
            else 'P' if t == 'asset' or t == 'liability' else 'M'
        amntTp = lambda c, d: 'C' if c > d else 'D' if d > c else 'C'
        amnt = lambda c, d: '{0:.02f}'.format(abs(d - c))
        totalDebit = lambda: '{0:.02f}'.format(
            sum(l.debit for j in journals for m in journals_moves[j.id] for l in m.line_id)
        )
        totalCredit = lambda: '{0:.02f}'.format(
            sum(l.credit for j in journals for m in journals_moves[j.id] for l in m.line_id)
        )
        periodNumber = lambda p: '{0:03d}'.format(
            datetime.datetime.strptime(p.date_start, _date_format).month
        )
        linesCount = lambda: sum(len(m.line_id) for j in journals for m in journals_moves[j.id])
        text = lambda t: '' if not t else t
        vat = lambda t: [] if not t or t not in tax_codes else [t]
        currency = lambda c: [] if not c else [c]
        vatPerc = lambda p: '{0:.03f}'.format(p)
        vatAmnt = lambda a: '{0:.02f}'.format(a)
        curAmnt = lambda a: '{0:.02f}'.format(a)
        curAmntDeb = lambda c, d, e: e if d > c else 0 if d < c else 0
        curAmntCred = lambda c, d, e: e if c > d else 0 if c < d else 0

        template = self.pool.get("xml.template")

        self._logger.info('create xml_template')
        template_id = template.create(cr, uid, {'name': data.name, 'content': data.template_content}, context=context)
        try:

            xml = template.generate_xml(
                cr, uid, template_id,
                partners=partners,
                fiscal_year=fiscal_year,
                date_created=datetime.date.today().strftime(_date_format),
                software_desc=release.description,
                software_version=release.major_version,
                company=partners[0].company_id,
                periods=periods,
                accounts=accounts,
                chartOfAccount=coa,
                linesCount=linesCount,
                journals=journals,
                journals_moves=journals_moves,
                tax_codes=tax_codes_list,
                custSupTp=custSupTp,
                accTp=accTp,
                amntTp=amntTp,
                amnt=amnt,
                totalDebit=totalDebit,
                totalCredit=totalCredit,
                periodNumber=periodNumber,
                text=text,
                vat=vat,
                currency=currency,
                vatPerc=vatPerc,
                vatAmnt=vatAmnt,
                curAmnt=curAmnt,
                curAmntDeb=curAmntDeb,
                curAmntCred=curAmntCred,
                empty="",
            )

            # validates given xml file
            self._logger.info('validate xml')
            _file = get_module_resource(
                'l10n_nl_xaf_auditfile_export', 'data', 'auditfile_schema.xsd')
            if not _file:
                raise Warning(_('Data Error'), _('Invalid XML schema'))
            _schema_doc = etree.parse(open(_file))
            _schema = etree.XMLSchema(_schema_doc)
            if not _schema.validate(xml):
                for line in _schema.error_log:
                    self._logger.error('%s\n' % line.message)
                raise Warning(_('Data Error'), _('Invalid Data. Please, see logs for details.'))

            # remove 'nso:' from file
            [xml_string] = etree.tostringlist(xml)
            xml_string = xml_string.replace("ns0:", "")
            xml_new = etree.fromstring(xml_string, parser=None, base_url=None)

            # attaches xml to module
            template.attach_xml(
                cr, uid, template_id, attach_to=data, xml=xml_new, name=data.name + _output_file,
                fname=data.name + _output_file,
                description='XML file representing this partner',
            )
            self._logger.info('auditfile_export created succesfully')
            self.write(cr, uid, ids[0],
                       {'date_printed': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)

        except Exception, e:
            self._logger.error(sys.exc_info())
            raise Warning(_('Data Error'), _('Invalid Data.\n%s\nPlease, see logs for details.') % e)

        self._logger.info('unlink xml_template')
        template.unlink(cr, uid, template_id, context=context)
        return True
