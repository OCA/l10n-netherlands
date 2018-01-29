# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "l10n_nl_country_states",
    "version": "10.0.1.0.1",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Dutch Localization",
    "depends": [
        'base',
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/l10n_nl_country_states.xml',
        "data/res_country_state_nl_zip.xml",
    ],
    "installable": True,
    "application": False,
}
