# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013-2014 Therp BV (<http://therp.nl>).
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
from openerp.osv.orm import Model
from openerp.osv import fields


class res_partner(Model):
    _inherit = 'res.partner'

    def _prepare_name_custom(self, cursor, uid, partner, context=None):
        name_template = Template(
            context.get(
                'name_format',
                "${p.firstname or p.initials or ''}"
                "${(p.firstname or p.initials) and ' ' or ''}"
                "${p.infix or ''}${p.infix and ' ' or ''}${p.lastname}"))
        name = name_template.render(p=partner)
        return (name[0] + name[1:]) if name else ''

    _columns = {
        'initials': fields.char('Initials', size=16),
        'infix': fields.char('Infix', size=32),
    }

    def _register_hook(self, cr):
        # if firstname_display_name_trigger is installed, add our keys to
        # the trigger
        if hasattr(self, '_display_name_store_triggers'):
            if self._name not in self._display_name_store_triggers:
                return
            self._display_name_store_triggers[self._name][1].extend(
                ['infix', 'initials'])
            for trigger in self.pool._store_function[self._name]:
                if trigger[0] != self._name or trigger[1] != 'display_name':
                    continue
                self.pool._store_function[self._name].append(
                    trigger[:3] +
                    ((trigger[3] + ('infix', 'initials')), ) +
                    trigger[4:])
                self.pool._store_function[self._name].remove(trigger)
                break
