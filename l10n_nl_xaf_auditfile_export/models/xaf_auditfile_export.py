# Copyright 2015 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import collections
import logging
import os
import shutil
import sys
import time
import traceback
import zipfile
from datetime import datetime, timedelta
from io import BytesIO
from tempfile import mkdtemp

import psutil
from dateutil.rrule import MONTHLY, rrule
from lxml import etree

from odoo import _, api, exceptions, fields, models, modules, release


def chunks(items, n=None):
    """Yield successive n-sized chunks from items."""
    if n is None:
        n = models.PREFETCH_MAX
    for i in range(0, len(items), n):
        yield items[i : i + n]


def memory_info():
    """Modified from odoo/server/service.py"""
    process = psutil.Process(os.getpid())
    pmem = (getattr(process, "memory_info", None) or process.get_memory_info)()
    return pmem.vms


# http://stackoverflow.com/questions/1707890
# /fast-way-to-filter-illegal-xml-unicode-chars-in-python
ILLEGAL_RANGES = [
    (0x00, 0x08),
    (0x0B, 0x1F),
    (0x7F, 0x84),
    (0x86, 0x9F),
    (0xD800, 0xDFFF),
    (0xFDD0, 0xFDDF),
    (0xFFFE, 0xFFFF),
    (0x1FFFE, 0x1FFFF),
    (0x2FFFE, 0x2FFFF),
    (0x3FFFE, 0x3FFFF),
    (0x4FFFE, 0x4FFFF),
    (0x5FFFE, 0x5FFFF),
    (0x6FFFE, 0x6FFFF),
    (0x7FFFE, 0x7FFFF),
    (0x8FFFE, 0x8FFFF),
    (0x9FFFE, 0x9FFFF),
    (0xAFFFE, 0xAFFFF),
    (0xBFFFE, 0xBFFFF),
    (0xCFFFE, 0xCFFFF),
    (0xDFFFE, 0xDFFFF),
    (0xEFFFE, 0xEFFFF),
    (0xFFFFE, 0xFFFFF),
    (0x10FFFE, 0x10FFFF),
]
UNICODE_SANITIZE_TRANSLATION = {}
for low, high in ILLEGAL_RANGES:
    if low > sys.maxunicode:  # pragma: no cover
        continue
    for c in range(low, high + 1):
        UNICODE_SANITIZE_TRANSLATION[c] = ord(" ")


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
    auditfile_success = fields.Boolean(copy=False)
    date_generated = fields.Datetime("Date generated", readonly=True, copy=False)

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        company = self.env.company
        fy_dates = company.compute_fiscalyear_dates(datetime.now())
        defaults.setdefault("date_start", fy_dates["date_from"])
        defaults.setdefault("date_end", fy_dates["date_to"])
        if "company_id" in fields_list:
            defaults.setdefault("company_id", company.id)
        if "name" in fields_list:
            defaults.setdefault(
                "name",
                _("Auditfile %(company_name)s %(current_datetime)s")
                % {
                    "company_name": company.name,
                    "current_datetime": datetime.now().strftime("%Y"),
                },
            )
        return defaults

    @api.constrains("date_start", "date_end")
    def check_dates(self):
        for auditfile in self:
            if auditfile.date_start >= auditfile.date_end:
                raise exceptions.ValidationError(
                    _("Starting date must be anterior ending date!")
                )

    @staticmethod
    def _get_auditfile_template():
        """return the qweb template to be rendered"""
        return "l10n_nl_xaf_auditfile_export.auditfile_template"

    def button_generate(self):
        t0 = time.time()
        m0 = memory_info()
        self.date_generated = fields.Datetime.now()
        auditfile_template = self._get_auditfile_template()
        xml = self.env["ir.qweb"]._render(
            auditfile_template, {"self": self}, minimal_qcontext=True
        )
        # convert to string and prepend XML encoding declaration
        xml = (
            xml.unescape()
            .strip()
            .replace(
                "<auditfile ",
                '<?xml version="1.0" encoding="UTF-8"?>\n<auditfile ',
                1,
            )
        )
        # removes invalid characters from xml
        if not self.env.context.get("dont_sanitize_xml"):
            xml = xml.translate(UNICODE_SANITIZE_TRANSLATION)

        filename = self.name + ".xaf"
        filename = filename.replace(os.sep, " ")
        tmpdir = mkdtemp()
        auditfile = os.path.join(tmpdir, filename)
        archivedir = mkdtemp()
        archive = os.path.join(archivedir, filename)
        self.auditfile_success = False
        try:
            with open(auditfile, "w+") as tmphandle:
                tmphandle.write(xml)
            del xml

            logging.getLogger(__name__).debug(
                "Created an auditfile in %ss, using %sk memory",
                int(time.time() - t0),
                (memory_info() - m0) / 1024,
            )

            # Store in compressed format on the auditfile record
            zip_path = shutil.make_archive(archive, "zip", tmpdir, verbose=True)
            with open(zip_path, "rb") as auditfile_zip:
                self.auditfile = base64.b64encode(auditfile_zip.read())
            logging.getLogger(__name__).debug(
                "Created an auditfile in %ss, using %sk memory",
                int(time.time() - t0),
                (memory_info() - m0) / 1024,
            )

            # Validate the generated XML
            xsd = etree.XMLSchema(
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
            xsd.assertValid(etree.parse(auditfile))
            del xsd

            self.auditfile_success = True

        except (etree.XMLSyntaxError, etree.DocumentInvalid) as e:
            logging.getLogger(__name__).error(e)
            logging.getLogger(__name__).info(traceback.format_exc())
            self.message_post(body=e)
            self.auditfile_success = False

        finally:
            shutil.rmtree(tmpdir)
            shutil.rmtree(archivedir)

    @staticmethod
    def get_odoo_version():
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
        self.env["res.partner"].invalidate_model()
        for chunk in chunks(partner_ids):
            yield from self.env["res.partner"].browse(chunk)
            self.env["res.partner"].invalidate_model()

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
        result = dict(credit=0.0, debit=0.0, count=0)
        for line in self.get_ob_lines():
            balance = line["balance"]
            if balance > 0:
                result["debit"] += balance
            else:
                result["credit"] -= balance
            result["count"] += 1
        return result

    def get_ob_lines(self):
        """return opening balance entries"""
        self.env.cr.execute(
            "select a.id, a.code, sum(l.balance) "
            "from account_move_line l, account_account a "
            "where a.id = l.account_id and l.date < %s "
            "and l.company_id=%s "
            "and l.parent_state = 'posted' "
            "and l.display_type NOT IN ('line_section', 'line_note') "
            "and a.include_initial_balance = true "
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
            "and parent_state = 'posted' "
            "and display_type NOT IN ('line_section', 'line_note') "
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
            "and parent_state = 'posted' "
            "and display_type NOT IN ('line_section', 'line_note') "
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
            "and parent_state = 'posted' "
            "and display_type NOT IN ('line_section', 'line_note') "
            "and company_id=%s",
            (self.date_start, self.date_end, self.company_id.id),
        )
        return round(self.env.cr.fetchall()[0][0] or 0.0, 2)

    def get_journals(self):
        """return journals"""
        return (
            self.env["account.journal"]
            .with_context(active_test=False)
            .search([("company_id", "=", self.company_id.id)])
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
                    ("state", "=", "posted"),
                ]
            )
            .ids
        )
        self.env["account.move"].invalidate_model()
        for chunk in chunks(move_ids):
            yield from self.env["account.move"].browse(chunk)
            self.env["account.move"].invalidate_model()

    @api.model
    def get_move_period_number(self, move):
        return self.get_period_number(move.date)
