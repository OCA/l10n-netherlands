# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api
from odoo import SUPERUSER_ID


def migrate(cr, version):
    '''
    Replace Tag "Voorbelasting (BTW) bis" with  Tag "5b. Voorbelasting (BTW)"
    '''
    env = api.Environment(cr, SUPERUSER_ID, {})

    tag_5b_btw = env.ref('l10n_nl.tag_nl_33', False)
    tag_5b_btw_bis = env.ref('l10n_nl.tag_nl_34', False)

    if tag_5b_btw and tag_5b_btw_bis:
        cr.execute('''
        UPDATE account_account_tag_account_tax_template_rel
            SET account_account_tag_id=%s
            WHERE account_account_tag_id=%s
        ''', (tag_5b_btw_bis.id, tag_5b_btw.id))
