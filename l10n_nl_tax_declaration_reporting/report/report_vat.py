# -*- coding: utf-8 -*-
# Copyright 2014-2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class VatReport(models.AbstractModel):
    _name = 'report.l10n_nl_tax_declaration_reporting.tax_report_template'

    @api.multi
    def render_html(self, data=None):

        company_id = data['form']['company_id']
        company_name = self.env['res.company'].browse(company_id).name

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']

        self.tax_report_lines = self._get_lines(data['form'])
        self.map_tax_tag = self._map_tax_tag(data['form'])

        self.tags_map = {}
        self.tags_map['1a'] = {'omzet': self.env.ref('l10n_nl.tag_nl_03').id,
                               'btw': self.env.ref('l10n_nl.tag_nl_20').id}
        self.tags_map['1b'] = {'omzet': self.env.ref('l10n_nl.tag_nl_05').id,
                               'btw': self.env.ref('l10n_nl.tag_nl_22').id}
        self.tags_map['1c'] = {'omzet': self.env.ref('l10n_nl.tag_nl_06').id,
                               'btw': self.env.ref('l10n_nl.tag_nl_23').id}
        self.tags_map['1d'] = {'omzet': self.env.ref('l10n_nl.tag_nl_07').id,
                               'btw': self.env.ref('l10n_nl.tag_nl_24').id}
        self.tags_map['1e'] = {'omzet': self.env.ref('l10n_nl.tag_nl_08').id}
        self.tags_map['2a'] = {'omzet': self.env.ref('l10n_nl.tag_nl_10').id,
                               'btw': self.env.ref('l10n_nl.tag_nl_27').id}
        self.tags_map['3a'] = {'omzet': self.env.ref('l10n_nl.tag_nl_12').id}
        self.tags_map['3b'] = {'omzet': self.env.ref('l10n_nl.tag_nl_13').id}
        self.tags_map['3c'] = {'omzet': self.env.ref('l10n_nl.tag_nl_14').id}
        self.tags_map['4a'] = {'omzet': self.env.ref('l10n_nl.tag_nl_16').id,
                               'btw': self.env.ref('l10n_nl.tag_nl_29').id}
        self.tags_map['4b'] = {'omzet': self.env.ref('l10n_nl.tag_nl_17').id,
                               'btw': self.env.ref('l10n_nl.tag_nl_30').id}
        self.tags_map['5b'] = {'btw': self.env.ref('l10n_nl.tag_nl_33').id}

        self.tax_code_error = ''
        _1AO = self._get_line_value('1a', 'omzet')
        _1AB = self._get_line_value('1a', 'btw')
        _1BO = self._get_line_value('1b', 'omzet')
        _1BB = self._get_line_value('1b', 'btw')
        _1CO = self._get_line_value('1c', 'omzet')
        _1CB = self._get_line_value('1c', 'btw')
        _1DO = self._get_line_value('1d', 'omzet')
        _1DB = self._get_line_value('1d', 'btw')
        _1EO = self._get_line_value('1e', 'omzet')
        _2AO = self._get_line_value('2a', 'omzet')
        _2AB = self._get_line_value('2a', 'btw')
        _3AO = self._get_line_value('3a', 'omzet')
        _3BO = self._get_line_value('3b', 'omzet')
        _3CO = self._get_line_value('3c', 'omzet')
        _4AO = self._get_line_value('4a', 'omzet')
        _4AB = self._get_line_value('4a', 'btw')
        _4BO = self._get_line_value('4b', 'omzet')
        _4BB = self._get_line_value('4b', 'btw')
        _5BB = self._get_line_value('5b', 'btw')

        _5AB = _1AB + _1BB + _1CB + _1DB + _2AB - _4AB - _4BB
        _5CB = _5AB - _5BB

        docargs = {
            'time_now': fields.Datetime.now(),
            'company': company_name,
            'start_date': date_from,
            'end_date': date_to,
            '_1AO': _1AO,
            '_1AB': _1AB,
            '_1BO': _1BO,
            '_1BB': _1BB,
            '_1CO': _1CO,
            '_1CB': _1CB,
            '_1DO': _1DO,
            '_1DB': _1DB,
            '_1EO': _1EO,
            '_2AO': _2AO,
            '_2AB': _2AB,
            '_3AO': _3AO,
            '_3BO': _3BO,
            '_3CO': _3CO,
            '_4AO': _4AO,
            '_4AB': _4AB,
            '_4BO': _4BO,
            '_4BB': _4BB,
            '_5AB': _5AB,
            '_5BB': _5BB,
            '_5CB': _5CB,
            'tax_code_error': self.tax_code_error,
        }

        return self.env['report'].render(
            'l10n_nl_tax_declaration_reporting.tax_report_template', docargs)

    def _get_line_value(self, code, type):
        tax_report_lines = self.tax_report_lines
        map_tax_tag = self.map_tax_tag
        tag_id = self.tags_map[code][type]
        for line in tax_report_lines:
            tax_id = line[0]
            tags_list = map_tax_tag[tax_id]
            if tag_id in tags_list:
                if type == 'omzet':
                    return line[2]
                return line[1]
        return 0.0

    def _map_tax_tag(self, form):

        query = """
            SELECT account_tax_id, account_account_tag_id
            FROM account_tax_account_tag
        """
        self._cr.execute(query)

        res = self._cr.fetchall()
        map = {}
        for row in res:
            key = row[0]
            if row[0] not in map:
                map[key] = [row[1]]
            else:
                map[key].append(row[1])
        return map

    def _get_lines(self, form):

        def filter_by_dates(date_from, date_to):
            where = 'WHERE inv.state IN (\'open\',\'paid\') '
            if date_from:
                where += " and inv.date >=  '" + date_from + "'"
            if date_to:
                where += " and inv.date <=  '" + date_to + "'"
            return where

        query = """
            SELECT inv_tax.tax_id,
                   sum(inv_tax.amount),
                   (
                    SELECT sum(price_subtotal_signed)
                    FROM account_invoice_line inv_line
                    JOIN account_invoice_line_tax inv_line_tax
                    ON inv_line.id = inv_line_tax.invoice_line_id
                    WHERE
                    inv_line.invoice_id = ANY(array_agg(inv_tax.invoice_id))
                    AND inv_line.id = inv_line_tax.invoice_line_id
                   )
            FROM account_invoice_tax AS inv_tax
                JOIN account_invoice inv
                    on inv.id = inv_tax.invoice_id
        """
        query += filter_by_dates(form['date_from'], form['date_to'])

        query += """
            AND inv.company_id = %s
            GROUP BY inv_tax.tax_id
        """
        self._cr.execute(query, (form['company_id'],))

        return self._cr.fetchall()
