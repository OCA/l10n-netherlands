# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models
try:
    from openerp.addons.field_char_transformed import FieldCharTransformed
except ImportError:
    pass


def _format_zipcode(zipcode):
    if not zipcode:
        return zipcode
    normalized = ''.join(zipcode.split())
    if len(normalized) == 6 and normalized[:4].isdigit() and\
       normalized[-2:].isalpha():
        return normalized[:4] + ' ' + normalized[-2:].upper()
    return zipcode


class ResPartner(models.Model):
    _inherit = 'res.partner'

    zip = FieldCharTransformed(transform=_format_zipcode)
