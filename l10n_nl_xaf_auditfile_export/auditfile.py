# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
"""All strings in this file should be in utf-8 encoding.

We will minimize data conversions. We read character data from postgress in
utf-8. We will write all data in utf-8. The strings we create in the file
(elements, formatted numeric data, dates) will only contain valid ascii
data, which is utf-8 by definition.

String manipulation, like taking substrings, should take care not to break
multibyte utf-8 characters. Therefore this manipulation needs to convert
byte strings to unicode, do the manipulation and then encode again to bytes.

We will write data to a file opened in binary mode, so we have to take care to
only write valid utf-8 encoded data. This also has to be safe for xml,
therefore needs to escape special character.
"""
from __future__ import generators

import argparse
import logging
import os
import psycopg2
import psycopg2.extras
import sys
from datetime import date
from xml.sax.saxutils import escape


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
_logger = logging.getLogger(__name__)


SQL_HEADER = \
    """SELECT y.code AS y_code,
    m.name AS m_name,
    to_char(CURRENT_DATE, 'YYYY-MM-DD') AS date_generated
 FROM account_period p
 LEFT OUTER JOIN account_fiscalyear y ON p.fiscalyear_id = y.id
 JOIN res_company c ON p.company_id = c.id
 LEFT OUTER JOIN res_currency m ON c.currency_id = m.id
 WHERE p.company_id = %(company_id)s
   AND p.date_start = %(date_start)s"""

SQL_COMPANY = \
    """SELECT c.id AS c_id, c.company_registry AS c_company_registry,
    p.name AS p_name,
    COALESCE(l.code, 'NL') AS l_code,
    COALESCE(p.vat, '') AS p_vat,
    COALESCE(p.street, '') AS p_street,
    COALESCE(p.city, '') AS p_city,
    COALESCE(s.name, '') AS s_name,
    COALESCE(p.zip, '') AS p_zip
 FROM res_company c
 JOIN res_partner p ON c.partner_id = p.id
 LEFT OUTER JOIN res_country_state s ON p.state_id = s.id
 LEFT OUTER JOIN res_country l ON p.country_id = l.id
 WHERE c.id = %(company_id)s"""

SQL_PARTNER_BANKS = \
    """SELECT a.acc_number AS a_acc_number,
    COALESCE(a.bank_bic, '') AS a_bank_bic,
    COALESCE(b.bic, '') AS b_bic
 FROM res_partner_bank a
 LEFT OUTER JOIN res_bank b ON a.bank = b.id
 WHERE a.partner_id = %(partner_id)s
 ORDER BY a.acc_number"""

SQL_PARTNERS = \
    """WITH first_contacts AS (
    SELECT p.id AS partner_id, MIN(c.id) AS contact_id
    FROM res_partner p
    JOIN res_partner c ON c.parent_id = p.id
    WHERE c.type = 'contact'
    GROUP BY p.id)
SELECT p.id AS p_id, p.name AS p_name,
    COALESCE(a.name, '') AS a_name,
    COALESCE(p.phone, '') AS p_phone,
    COALESCE(p.fax, '') AS p_fax,
    COALESCE(p.email, '') AS p_email,
    COALESCE(p.website, '') AS p_website,
    COALESCE(l.code, 'NL') AS l_code,
    COALESCE(p.vat, '') AS p_vat,
    COALESCE(p.customer, false) AS p_customer,
    COALESCE(p.supplier, false) AS p_supplier,
    COALESCE(p.credit_limit, 0.0) AS p_credit_limit,
    COALESCE(p.street, '') AS p_street,
    COALESCE(p.city, '') AS p_city,
    COALESCE(p.zip, '') AS p_zip,
    COALESCE(s.name, '') AS s_name,
    to_char(COALESCE(p.write_date, p.create_date), 'YYYY-MM-DD HH24:MI:SS')
        AS last_change,
    COALESCE(w.login, c.login, '') as last_change_login
 FROM res_partner p
 LEFT OUTER JOIN first_contacts f ON p.id = f.partner_id
 LEFT OUTER JOIN res_partner a ON f.contact_id = a.id
 LEFT OUTER JOIN res_country_state s ON p.state_id = s.id
 LEFT OUTER JOIN res_country l ON p.country_id = l.id
 LEFT OUTER JOIN res_users w ON p.write_uid = w.id
 LEFT OUTER JOIN res_users c ON p.create_uid = c.id
 WHERE p.company_id = %(company_id)s OR p.company_id IS NULL
 ORDER BY p.name"""

SQL_ACCOUNTS = \
    """SELECT a.code AS a_code, a.name AS a_name,
    t.report_type AS t_report_type,
    to_char(COALESCE(a.write_date, a.create_date), 'YYYY-MM-DD HH24:MI:SS')
        AS last_change,
    COALESCE(w.login, c.login, '') as last_change_login
 FROM account_account a
 JOIN account_account_type t ON a.user_type = t.id
 LEFT OUTER JOIN res_users w ON a.write_uid = w.id
 LEFT OUTER JOIN res_users c ON a.create_uid = c.id
 WHERE a.company_id = %(company_id)s
   AND a.type <> 'view'
 ORDER BY a.code"""

SQL_VATCODES = \
    """SELECT t.id AS t_id, t.name AS t_name,
    p.code AS p_code, c.code AS c_code
 FROM account_tax t
 JOIN account_account p ON t.account_paid_id = p.id
 JOIN account_account c ON t.account_collected_id = c.id
 WHERE p.company_id = %(company_id)s
 ORDER BY t.name"""

SQL_PERIODS = \
    """SELECT p.id AS p_id, p.name AS p_name,
    p.date_start AS p_date_start, p.date_stop AS p_date_stop
 FROM account_period p
 WHERE p.company_id = %(company_id)s
   AND p.date_start >= %(date_start)s
   AND p.date_stop <= %(date_stop)s
 ORDER BY p.date_start"""

SQL_TRANSACTION_SUMMARY = \
    """WITH selected_periods AS (
    SELECT p.id, p.name, p.date_start
    FROM account_period p
    WHERE p.company_id = %(company_id)s
      AND p.date_start >= %(date_start)s
      AND p.date_stop <= %(date_stop)s)
 SELECT
        count(*) as t_count,
        COALESCE(SUM(debit), 0.0) AS t_debit,
        COALESCE(SUM(credit), 0.0) AS t_credit
    FROM account_move_line l
    JOIN account_move m ON l.move_id = m.id
    JOIN selected_periods p ON l.period_id = p.id
    WHERE m.state = 'posted'
      AND l.state = 'valid'
      AND (l.debit <> 0.0 OR l.credit <> 0.0)"""

SQL_TRANSACTIONS = \
    """WITH selected_periods AS (
    SELECT p.id, p.name, p.date_start
    FROM account_period p
    WHERE p.company_id = %(company_id)s
      AND p.date_start >= %(date_start)s
      AND p.date_stop <= %(date_stop)s),
 transaction_totals AS (
    SELECT l.move_id AS tt_id, SUM(l.debit) as tt_amount
    FROM account_move_line l
    JOIN selected_periods p ON l.period_id = p.id
    GROUP BY l.move_id)
 SELECT
     j.id AS j_id, j.code AS j_code, j.name AS j_name, j.type AS j_type,
     m.id AS m_id, m.name AS m_name, m.date AS m_date,
     tt_amount,
     p.id AS p_id, p.date_start AS p_date_start, p.name AS p_name,
     l.id AS l_id, l.name AS l_name, COALESCE(l.ref, '')  as l_ref,
     l.date as l_date, l.partner_id AS l_partner_id,
     l.debit AS l_debit, l.credit AS l_credit,
     l.amount_currency AS l_amount_currency,
     a.code AS a_code,
     COALESCE(r.name, '') AS r_name,
     COALESCE(i.number, '') AS i_number,
     COALESCE(c.name, '') AS c_name
 FROM account_move m
 JOIN selected_periods p ON m.period_id = p.id
 JOIN transaction_totals tt ON tt_id = m.id
 JOIN account_journal j ON m.journal_id = j.id
 JOIN account_move_line l ON m.id = l.move_id
 JOIN account_account a ON l.account_id = a.id
 LEFT OUTER JOIN account_move_reconcile r ON l.reconcile_id = r.id
 LEFT OUTER JOIN account_invoice i ON m.id = i.move_id
 LEFT OUTER JOIN res_currency c ON l.currency_id = c.id
 WHERE m.state = 'posted'
   AND l.state = 'valid'
   AND (l.debit <> 0.0 OR l.credit <> 0.0)
 ORDER BY j.code, m.date, m.id, a.code"""


def ResultIter(cursor, arraysize=1000):
    'An iterator that uses fetchmany to keep memory usage down'
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result


def get_element(element_name, value, max_length=0, optional=False):
    if optional and not value:
        return ''
    if not value:
        # empty element
        return "<%(element_name)s />" % {'element_name': element_name}
    # Force value to unicode string to allow manipulation
    if isinstance(value, unicode):
        pass
    elif isinstance(value, basestring):
        value = unicode(value, 'utf8')
    else:
        value = unicode("%s" % value)
    # shorten
    value = value.strip()
    if max_length:
        value = value[:max_length]
    # Back from unicode to utf-8 encoded string
    value = value.encode('utf8')
    value = escape(value)  # convert to xml safe string
    return "<%(element_name)s>%(value)s</%(element_name)s>" % {
        'element_name': element_name, 'value': value}


def get_element_xml(element_name, value, optional=False):
    """Get element for value that already contains valix xml."""
    if optional and not value:
        return ''
    if not value:
        # empty element
        return "<%(element_name)s />" % {'element_name': element_name}
    return "<%(element_name)s>%(value)s</%(element_name)s>" % {
        'element_name': element_name, 'value': value}


def writeln_element(
        outfile, element_name, value, indent=0, max_length=0, optional=False):
    if optional and not value:
        return ''
    if indent:
        outfile.write(' ' * indent)
    outfile.write(get_element(element_name, value, max_length=max_length))
    outfile.write('\n')


def writeln_element_xml(outfile, element_name, value, indent=0):
    """Use this for data that is known to be already xml."""
    outfile.write(
        "%(indent)s<%(element_name)s>%(value)s</%(element_name)s>\n" % {
            'indent': ' ' * indent,
            'element_name': element_name,
            'value': value})


def writeln_element_open(outfile, element_name, indent=0):
    if indent:
        outfile.write(' ' * indent)
    outfile.write('<%s>\n' % element_name)


def writeln_element_close(outfile, element_name, indent=0):
    if indent:
        outfile.write(' ' * indent)
    outfile.write('</%s>\n' % element_name)


def writeln_element_empty(outfile, element_name, indent=0):
    if indent:
        outfile.write(' ' * indent)
    outfile.write('<%s />\n' % element_name)


def write_data(outfile, data, indent=0):
    """data contains an array of tuples that must be written as
    elements.
    Each tuple contains at least an element_name.
    If the tuple has a second element it is the value.
    If the tuple has a third element, it is the max_length of the value.
    """
    for element in data:
        element_name = element[0]
        value = len(element) > 1 and element[1] or ''
        max_length = len(element) > 2 and element[2] or 0
        writeln_element(
            outfile, element_name, value, indent=indent,
            max_length=max_length)


def write_header(specification, outfile, connection):
    outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    outfile.write(
        '<auditfile'
        ' xmlns="http://www.auditfiles.nl/XAF/3.2"'
        ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n')
    writeln_element_open(outfile, 'header', indent=2)
    with connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(SQL_HEADER, specification)
        row = cursor.fetchone()
        data = (
            ('fiscalYear', row['y_code'], 9),
            ('startDate', specification['date_start']),
            ('endDate', specification['date_stop']),
            ('curCode', row['m_name']),
            ('dateCreated', row['date_generated']),
            ('softwareDesc', 'Odoo'),
            ('softwareVersion', '8.0'))
        write_data(outfile, data, indent=4)
    writeln_element_close(outfile, 'header', indent=2)


def patch_country_code(country_code):
    """Not all countrycodes are already in the xsd schema.

    JE - Jersey
    ME - Montenegro
    """
    if country_code in ['JE', 'ME']:
        return 'NL'
    return country_code


def write_partner_street(row, outfile):
    writeln_element_open(outfile, 'streetAddress', indent=6)
    data = (
        ('streetname', row['p_street'], 999),
        ('number', ),
        ('numberExtension', ),
        ('property', ),
        ('city', row['p_city'], 50),
        ('postalCode', row['p_zip'], 10),
        ('region', row['s_name'], 50),
        ('country', patch_country_code(row['l_code'])))
    write_data(outfile, data, indent=8)
    writeln_element_close(outfile, 'streetAddress', indent=6)


def write_company_header(specification, outfile, connection):
    writeln_element_open(outfile, 'company', indent=2)
    with connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(SQL_COMPANY, specification)
        row = cursor.fetchone()
        data = (
            ('companyIdent', row['c_company_registry']),
            ('companyName', row['p_name'], 50),
            ('taxRegistrationCountry', row['l_code']),
            ('taxRegIdent', row['p_vat'], 30))
        write_data(outfile, data, indent=4)
        write_partner_street(row, outfile)


def write_partner_bank_accounts(partner_id, outfile, connection):
    with connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor) as cursor:
        specification = {'partner_id': partner_id}
        cursor.execute(SQL_PARTNER_BANKS, specification)
        for row in cursor:
            bank_bic = row['a_bank_bic'] or row['b_bic'] or ''
            value = ''.join([
                get_element('bankAccNr', row['a_acc_number'], max_length=35),
                get_element('bankIdCd', bank_bic)])
            writeln_element_xml(outfile, 'bankAccount', value, indent=6)


def write_last_change_info(row, outfile):
    if row['last_change_login']:
        change_datetime = (
            "%sT%s" % (row['last_change'][:10], row['last_change'][-8:]))
        value = ''.join([
            get_element('userID', row['last_change_login']),
            get_element('changeDateTime', change_datetime),
            get_element('changeDescription', 'Last change')])
        writeln_element_xml(outfile, 'changeInfo', value, indent=6)


def write_partners(specification, outfile, connection):
    writeln_element_open(outfile, 'customersSuppliers', indent=4)
    with connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(SQL_PARTNERS, specification)
        for row in cursor:
            customer = row['p_customer']
            supplier = row['p_supplier']
            cs_type = (
                customer and supplier and 'B' or
                customer and 'C' or
                supplier and 'S' or 'O')
            writeln_element_open(outfile, 'customerSupplier', indent=6)
            data = (
                ('custSupID', row['p_id']),
                ('custSupName', row['p_name'], 50),
                ('contact', row['a_name'], 50),
                ('telephone', row['p_phone'], 30),
                ('fax', row['p_fax'], 30),
                ('eMail', row['p_email'], 30),
                ('website', row['p_website']),
                ('commerceNr', ),
                ('taxRegistrationCountry',
                 patch_country_code(row['l_code'])),
                ('taxRegIdent', row['p_vat'], 30),
                ('custSupTp', cs_type))
            write_data(outfile, data, indent=6)
            if customer and row['p_credit_limit']:
                writeln_element(
                    outfile, 'custCreditLimit', row['p_credit_limit'],
                    indent=6)
            if supplier and row['p_credit_limit']:
                writeln_element(
                    outfile, 'supplierLimit', row['p_credit_limit'],
                    indent=6)
            write_partner_street(row, outfile)
            write_partner_bank_accounts(row['p_id'], outfile, connection)
            write_last_change_info(row, outfile)
            writeln_element_empty(
                outfile, 'customerSupplierHistory', indent=6)
            writeln_element_close(outfile, 'customerSupplier', indent=6)
    writeln_element_close(outfile, 'customersSuppliers', indent=4)


def write_general_ledger(specification, outfile, connection):
    writeln_element_open(outfile, 'generalLedger', indent=4)
    with connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(SQL_ACCOUNTS, specification)
        for row in cursor:
            writeln_element_open(outfile, 'ledgerAccount', indent=6)
            report_type = row['t_report_type']
            acc_type = (
                report_type in ['income', 'expense'] and 'P' or
                report_type in ['asset', 'liability'] and 'B' or 'M')
            data = (
                ('accID', row['a_code']),
                ('accDesc', row['a_name'], 999),
                ('accTp', acc_type))
            write_data(outfile, data, indent=8)
            write_last_change_info(row, outfile)
            writeln_element_empty(outfile, 'glAccountHistory', indent=6)
            writeln_element_close(outfile, 'ledgerAccount', indent=6)
    writeln_element_close(outfile, 'generalLedger', indent=4)


def write_vatcodes(specification, outfile, connection):
    writeln_element_open(outfile, 'vatCodes', indent=4)
    with connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(SQL_VATCODES, specification)
        for row in cursor:
            value = ''.join([
                get_element('vatID', row['t_id']),
                get_element('vatDesc', row['t_name'], max_length=999),
                get_element('vatToPayAccID', row['p_code']),
                get_element('vatToClaimAccID', row['c_code'])])
            writeln_element_xml(outfile, 'vatCode', value, indent=6)
    writeln_element_close(outfile, 'vatCodes', indent=4)


def write_periods(specification, outfile, connection):
    writeln_element_open(outfile, 'periods', indent=4)
    with connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(SQL_PERIODS, specification)
        for row in cursor:
            value = ''.join([
                get_element('periodNumber', row['p_id']),
                get_element('periodDesc', row['p_name']),
                get_element('startDatePeriod', row['p_date_start']),
                get_element('endDatePeriod', row['p_date_stop'])])
            writeln_element_xml(outfile, 'period', value, indent=6)
    writeln_element_close(outfile, 'periods', indent=4)


def write_transactions_header(specification, outfile, connection):
    writeln_element_open(outfile, 'transactions', indent=4)
    with connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(SQL_TRANSACTION_SUMMARY, specification)
        row = cursor.fetchone()
        data = (
            ('linesCount', row['t_count']),
            ('totalDebit', row['t_debit']),
            ('totalCredit', row['t_credit']))
        write_data(outfile, data, indent=6)


def write_journal_header(outfile, row):
    writeln_element_open(outfile, 'journal', indent=4)
    TYPE_TABLE = {
        'bank': 'B',
        'cash': 'C',
        'situation': 'O',
        'sale': 'S',
        'sale_refund': 'S',
        'purchase': 'P',
        'purchase_refund': 'P'}
    j_type = row['j_type']
    journal_type = j_type in TYPE_TABLE and TYPE_TABLE[j_type] or 'Z'
    data = (
        ('jrnID', row['j_code']),
        ('desc', row['j_name']),
        ('jrnTp', journal_type))
    write_data(outfile, data, indent=6)
    return row['j_id']


def write_transaction_header(outfile, row):
    writeln_element_open(outfile, 'transaction', indent=6)
    data = (
        ('nr', row['m_id']),
        ('desc', row['m_name']),
        ('periodNumber', row['p_id']),
        ('trDt', row['m_date']),
        ('amnt', row['tt_amount']))
    write_data(outfile, data, indent=8)
    return row['m_id']


def write_row(outfile, row):
    debit = row['l_debit']
    credit = row['l_credit']
    if credit > 0.0:
        amount = credit
        sign = 'C'
    else:
        amount = debit
        sign = 'D'
    if row['c_name'] and row['l_amount_currency']:
        currency_value = (
            get_element('curCode', row['c_name']) +
            get_element('curAmnt', row['l_amount_currency']))
    else:
        currency_value = ''
    value = ''.join([
        get_element('nr', row['l_id']),
        get_element('accID', row['a_code']),
        get_element('docRef', row['l_ref'], max_length=999),
        get_element('effDate', row['l_date']),
        get_element('desc', row['l_name']),
        get_element('amnt', "%13.2f" % amount),
        get_element('amntTp', sign),
        get_element('recRef', row['r_name'], optional=True),
        get_element('custSupID', row['l_partner_id'], optional=True),
        get_element('invRef', row['i_number'], max_length=999, optional=True),
        get_element_xml('currency', currency_value, optional=True)])
    writeln_element_xml(outfile, 'trLine', value, indent=8)


def write_transaction_footer(outfile):
    writeln_element_close(outfile, 'transaction', indent=6)


def write_journal_footer(outfile):
    writeln_element_close(outfile, 'journal', indent=4)


def write_transactions_footer(outfile):
    writeln_element_close(outfile, 'transactions', indent=2)


def write_footer(outfile):
    writeln_element_close(outfile, 'company')
    writeln_element_close(outfile, 'auditfile')


def write_transactions(specification, outfile, connection):
    write_transactions_header(specification, outfile, connection)
    with connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(SQL_TRANSACTIONS, specification)
        iter_cursor = ResultIter(cursor)
        row = next(iter_cursor, None)
        while row:
            # Handle journal header level
            j_id = write_journal_header(outfile, row)
            while row and j_id == row['j_id']:
                # Handle transaction header level
                m_id = write_transaction_header(outfile, row)
                while row and j_id == row['j_id'] and m_id == row['m_id']:
                    # Handle transaction detail level
                    write_row(outfile, row)
                    row = next(iter_cursor, None)
                write_transaction_footer(outfile)
            write_journal_footer(outfile)
    write_transactions_footer(outfile)


def create_auditfile(specification, file_name, connection_string):
    """Create xml audit file from transactions."""
    with open(file_name, "wb", 1) as outfile:  # line buffering
        with psycopg2.connect(connection_string) as connection:
            connection.set_client_encoding('utf8')
            write_header(specification, outfile, connection)
            write_company_header(specification, outfile, connection)
            write_partners(specification, outfile, connection)
            write_general_ledger(specification, outfile, connection)
            write_vatcodes(specification, outfile, connection)
            write_periods(specification, outfile, connection)
            write_transactions(specification, outfile, connection)
            write_footer(outfile)
        connection.close()  # Not done at end of with block


def main():

    def parse_arguments():
        parser = argparse.ArgumentParser()
        # Pass connection string as:
        # "dbname='template1' user='my_user' host='localhost' password='password'"
        # Only dbname is required (when using ident login)
        parser.add_argument('connection_string', action='store')
        # Compute default start and end date
        today = date.today()
        firstday = date(today.year, 1, 1)
        parser.add_argument(
            '-s', '--start-date', action='store', dest='start_date',
            default=firstday.strftime('%Y-%m-%d'))
        parser.add_argument(
            '-e', '--end-date', action='store', dest='end_date',
            default=today.strftime('%Y-%m-%d'))
        return parser.parse_args()

    args = parse_arguments()
    try:
        specification = {
            'company_id': 1,
            'date_start': args.start_date,
            'date_stop': args.end_date}
        connection_string = args.connection_string
        create_auditfile(specification, 'auditfile.xaf', connection_string)
        return 0
    except Exception as err:
        _logger.exception('Unexpected exception in main()')
        return 2


if __name__ == "__main__":
    sys.exit(main())
