# Copyright 2016-2017 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID


def set_unece_on_taxes(cr, _):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for company in env['res.company'].search([
            ("partner_id.country_id", "=", env.ref("base.nl").id),
        ]):
            company._l10n_nl_set_unece_on_taxes()
