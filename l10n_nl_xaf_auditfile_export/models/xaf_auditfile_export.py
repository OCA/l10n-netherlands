# Copyright 2015 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import collections
import logging
import os
import shutil
import time
import zipfile
from datetime import datetime, timedelta
from io import BytesIO
from tempfile import mkdtemp

import psutil
from dateutil.rrule import MONTHLY, rrule
from lxml import etree

from odoo import _, api, exceptions, fields, models, modules, release


def chunks(l, n=None):
    """Yield successive n-sized chunks from l."""
    if n is None:
        n = models.PREFETCH_MAX
    for i in range(0, len(l), n):
        yield l[i : i + n]


def memory_info():
    """ Modified from odoo/server/service.py """
    process = psutil.Process(os.getpid())
    pmem = (getattr(process, "memory_info", None) or process.get_memory_info)()
    return pmem.vms


class XafAuditfileExport(models.Model):
    _name = "xaf.auditfile.export"
    _description = "XAF auditfile export"
    _inherit = ["mail.thread"]
    _order = "date_start desc"

    @api.depends("name", "auditfile")
    def _compute_auditfile_name(self):
        for item in self:
            item.auditfile_name = "%s.xaf" % item.name
            if item.auditfile:
                auditfile = base64.b64decode(item.auditfile)
                zf = BytesIO(auditfile)
                if zipfile.is_zipfile(zf):
                    item.auditfile_name += ".zip"

    def _compute_fiscalyear_name(self):
        for auditfile in self:
            if auditfile.date_start:
                auditfile.fiscalyear_name = auditfile.date_start.year

    name = fields.Char()
    date_start = fields.Date("Start date", required=True)
    date_end = fields.Date("End date", required=True)
    fiscalyear_name = fields.Char(compute="_compute_fiscalyear_name")
    auditfile = fields.Binary(readonly=True, copy=False)
    auditfile_name = fields.Char(
        "Auditfile filename", compute="_compute_auditfile_name", store=True
    )
    date_generated = fields.Datetime("Date generated", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", required=True)

    unit4 = fields.Boolean(
        help="The Unit4 system expects a value for "
        '`<xsd:element name="docRef" ..>` of maximum 35 characters, '
        "infringing the official standard. In case the value exceeds 35 "
        "characters, an error is raised by Unit4 while importing the "
        "audit file. By setting this flag to true, the `docRef` value "
        "is simply truncated to 35 characters so that the auditfile can "
        "be successfully imported into Unit4.\n"
        "If you want to export an auditfile with the official standard "
        "(missing the Unit4 compatibility) just set this flag to False."
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        company = self.env.user.company_id
        fy_dates = company.compute_fiscalyear_dates(datetime.now())
        defaults.setdefault("date_start", fy_dates["date_from"])
        defaults.setdefault("date_end", fy_dates["date_to"])
        if "company_id" in fields_list:
            defaults.setdefault("company_id", company.id)
        if "name" in fields_list:
            defaults.setdefault(
                "name",
                _("Auditfile %s %s") % (company.name, datetime.now().strftime("%Y")),
            )

        return defaults

    @api.constrains("date_start", "date_end")
    def check_dates(self):
        for auditfile in self:
            if auditfile.date_start >= auditfile.date_end:
                raise exceptions.ValidationError(
                    _("Starting date must be anterior ending date!")
                )

    def _get_auditfile_template(self):
        """return the qweb template to be rendered"""
        return "l10n_nl_xaf_auditfile_export.auditfile_template"

    def button_generate(self):
        t0 = time.time()
        m0 = memory_info()
        self.date_generated = fields.Datetime.now()
        auditfile_template = self._get_auditfile_template()
        xml = self.env["ir.ui.view"].render_template(
            auditfile_template, values={"self": self}
        )
        # the following is dealing with the fact that qweb templates don't like
        # namespaces, but we need the correct namespaces for validation
        xml = (
            xml.decode()
            .strip()
            .replace(
                "<auditfile>",
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<auditfile xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                'xmlns="http://www.auditfiles.nl/XAF/3.2">',
                1,
            )
        )

        filename = self.name + ".xaf"
        filename = filename.replace(os.sep, " ")
        tmpdir = mkdtemp()
        auditfile = os.path.join(tmpdir, filename)
        archivedir = mkdtemp()
        archive = os.path.join(archivedir, filename)
        try:
            with open(auditfile, "w+") as tmphandle:
                tmphandle.write(xml)
            del xml

            # Validate the generated XML
            xsd = etree.XMLParser(
                schema=etree.XMLSchema(
                    etree.parse(
                        open(
                            modules.get_resource_path(
                                "l10n_nl_xaf_auditfile_export",
                                "data",
                                "XmlAuditfileFinancieel3.2.xsd",
                            )
                        )
                    )
                )
            )
            etree.parse(auditfile, parser=xsd)
            del xsd

            # Store in compressed format on the auditfile record
            zip_path = shutil.make_archive(archive, "zip", tmpdir, verbose=True)
            with open(zip_path, "rb") as auditfile_zip:
                self.auditfile = base64.b64encode(auditfile_zip.read())
            logging.getLogger(__name__).debug(
                "Created an auditfile in %ss, using %sk memory",
                int(time.time() - t0),
                (memory_info() - m0) / 1024,
            )

        except etree.XMLSyntaxError as e:
            logging.getLogger(__name__).error(e)
            self.message_post(body=e)
        finally:
            shutil.rmtree(tmpdir)
            shutil.rmtree(archivedir)

    def get_odoo_version(self):
        """return odoo version"""
        return release.version

    def get_partners(self):
        """return a generator over partners"""
        partner_ids = (
            self.env["res.partner"]
            .search(
                [
                    "|",
                    ("customer_rank", ">", 0),
                    ("supplier_rank", ">", 0),
                    "|",
                    ("company_id", "=", False),
                    ("company_id", "=", self.company_id.id),
                ]
            )
            .ids
        )
        self.env.cache.invalidate()
        for chunk in chunks(partner_ids):
            for partner in self.env["res.partner"].browse(chunk):
                yield partner
            self.env.cache.invalidate()

    def get_accounts(self):
        """return recordset of accounts"""
        return self.env["account.account"].search(
            [("company_id", "=", self.company_id.id)]
        )

    @api.model
    def get_period_number(self, date):
        year = date.strftime("%Y")[-1:]
        month = date.strftime("%m")
        return year + month

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
            freq=MONTHLY, bymonth=(), dtstart=self.date_start, until=self.date_end
        )

        Period = collections.namedtuple("Period", "number name date_start date_end")
        periods = []
        for dt_start in list(months):
            date_start = dt_start.date()
            date_end = month_end_date(dt_start.date())
            periods.append(
                Period(
                    number=self.get_period_number(date_start),
                    name=dt_start.strftime("%B") + " " + self.fiscalyear_name,
                    date_start=date_start,
                    date_end=date_end,
                )
            )

        return periods

    def get_taxes(self):
        """return taxes"""
        return self.env["account.tax"].search([("company_id", "=", self.company_id.id)])

    def get_ob_totals(self):
        """return totals of opening balance"""
        self.env.cr.execute(
            "select sum(l.credit), sum(l.debit), count(distinct a.id) "
            "from account_move_line l, account_account a, "
            "     account_account_type t "
            "where a.user_type_id = t.id "
            "and l.account_id = a.id "
            "and l.date < %s "
            "and l.company_id=%s "
            "and t.include_initial_balance = true ",
            (self.date_start, self.company_id.id),
        )
        row = self.env.cr.fetchall()[0]
        return dict(
            credit=round(row[0] or 0.0, 2),
            debit=round(row[1] or 0.0, 2),
            count=row[2] or 0,
        )

    def get_ob_lines(self):
        """return opening balance entries"""
        self.env.cr.execute(
            "select a.id, a.code, sum(l.balance) "
            "from account_move_line l, account_account a, "
            "     account_account_type t "
            "where a.user_type_id = t.id "
            "and a.id = l.account_id and l.date < %s "
            "and l.company_id=%s "
            "and t.include_initial_balance = true "
            "group by a.id, a.code",
            (self.date_start, self.company_id.id),
        )
        for result in self.env.cr.fetchall():
            yield dict(
                account_id=result[0],
                account_code=result[1],
                balance=round(result[2], 2),
            )

    def get_move_line_count(self):
        """return amount of move lines"""
        self.env.cr.execute(
            "select count(*) from account_move_line "
            "where date >= %s "
            "and date <= %s "
            "and company_id=%s",
            (self.date_start, self.date_end, self.company_id.id),
        )
        return self.env.cr.fetchall()[0][0]

    def get_move_line_total_debit(self):
        """return total debit of move lines"""
        self.env.cr.execute(
            "select sum(debit) from account_move_line "
            "where date >= %s "
            "and date <= %s "
            "and company_id=%s",
            (self.date_start, self.date_end, self.company_id.id),
        )
        return round(self.env.cr.fetchall()[0][0] or 0.0, 2)

    def get_move_line_total_credit(self):
        """return total credit of move lines"""
        self.env.cr.execute(
            "select sum(credit) from account_move_line "
            "where date >= %s "
            "and date <= %s "
            "and company_id=%s",
            (self.date_start, self.date_end, self.company_id.id),
        )
        return round(self.env.cr.fetchall()[0][0] or 0.0, 2)

    def get_journals(self):
        """return journals"""
        return self.env["account.journal"].search(
            [("company_id", "=", self.company_id.id)]
        )

    def get_moves(self, journal):
        """return moves for a journal, generator style"""
        move_ids = (
            self.env["account.move"]
            .search(
                [
                    ("date", ">=", self.date_start),
                    ("date", "<=", self.date_end),
                    ("journal_id", "=", journal.id),
                ]
            )
            .ids
        )
        self.env.cache.invalidate()
        for chunk in chunks(move_ids):
            for move in self.env["account.move"].browse(chunk):
                yield move
            self.env.cache.invalidate()

    @api.model
    def get_move_period_number(self, move):
        return self.get_period_number(move.date)
