# Copyright 2017-2018 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.osv import expression


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def get_move_line_partial_domain(self, from_date, to_date, company_id):
        res = super().get_move_line_partial_domain(
            from_date,
            to_date,
            company_id
        )

        if self.env.context.get('skip_invoice_basis_domain'):
            return res

        company = self.env['res.company'].browse(company_id)
        if company.country_id != self.env.ref('base.nl'):
            return res

        domain_params = {
            'company_id': company_id,
            'from_date': from_date,
            'to_date': to_date,
        }
        # following line breaks the inheritance chain;
        # it is intentional, to avoid other modules to interfere;
        # pass context ''skip_invoice_basis_domain' if you
        # don't want to allow this behavior
        return self._get_invoice_basis_domain(domain_params)

    def _get_invoice_basis_domain(self, domain_params):
        domain_company = [('company_id', '=', domain_params['company_id'])]
        domain_tax_date = self._get_tax_date_domain(domain_params)
        domain_account_date = self._get_accounting_date_domain(domain_params)
        domain_dates = expression.OR([domain_tax_date, domain_account_date])
        return expression.AND([domain_company, domain_dates])

    def _get_accounting_date_domain(self, domain_params):
        # if 'l10n_nl_date_invoice' is not set, get the account date instead
        return expression.AND([
            [('l10n_nl_date_invoice', '=', False)],
            [('date', '>=', domain_params['from_date'])],
            [('date', '<=', domain_params['to_date'])],
        ])

    def _get_tax_date_domain(self, domain_params):
        # if 'l10n_nl_date_invoice' is set, use this value
        # instead of the standard 'date'
        return expression.AND([
            [('l10n_nl_date_invoice', '!=', False)],
            [('l10n_nl_date_invoice', '>=', domain_params['from_date'])],
            [('l10n_nl_date_invoice', '<=', domain_params['to_date'])],
        ])
