# -*- coding: utf-8 -*-
# © 2016-2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID


def set_unece_on_taxes(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        companies = env['res.company'].search([])
        for company in companies:
            if company.country_id and company.country_id != env.ref('base.nl'):
                continue
            company._l10n_nl_set_unece_on_taxes()
    return
