# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, _):
    """Define Dutch specific configuration in res.country."""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        base_nl = env.ref('base.nl')
        _logger.info('Setting Netherlands NUTS configuration')
        base_nl.write({'state_level': 3})
