# Copyright 2020 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.l10n_nl_tax_statement.hooks import pre_init_hook


def migrate(cr, version):
    """ Precreate stored related fields introduced in this version
    """
    pre_init_hook(cr)
