# -*- coding: utf-8 -*-
"""Extend res.partner with extra fields for Dutch names."""
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013-2015 Therp BV <http://therp.nl>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from mako.template import Template
from openerp import models, fields


class ResPartner(models.Model):
    """Extend res.partner with extra fields for Dutch names."""
    _inherit = 'res.partner'

    initials = fields.Char(size=16)
    infix = fields.Char(size=32)

    def _prepare_name_custom(self, cursor, uid, partner, context=None):
        name_template = Template(
            context.get(
                'name_format',
                "${p.firstname or p.initials or ''}"
                "${(p.firstname or p.initials) and ' ' or ''}"
                "${p.infix or ''}${p.infix and ' ' or ''}${p.lastname}"))
        name = name_template.render(p=partner)
        return (name[0] + name[1:]) if name else ''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
