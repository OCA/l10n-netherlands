# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
from odoo import models


class IrQwebAuditfileStringWidget999(models.AbstractModel):
    _name = 'ir.qweb.field.auditfile.string999'
    _inherit = 'ir.qweb.field'
    _max_length = 999

    def _format(self, inner, options, qwebcontext):
        return self.pool['ir.qweb']\
            .eval_str(inner, qwebcontext)[:self._max_length]


class IrQwebAuditfileStringWidget9(models.AbstractModel):
    _name = 'ir.qweb.field.auditfile.string9'
    _inherit = 'ir.qweb.field.auditfile.string999'
    _max_length = 9


class IrQwebAuditfileStringWidget10(models.AbstractModel):
    _name = 'ir.qweb.field.auditfile.string10'
    _inherit = 'ir.qweb.field.auditfile.string999'
    _max_length = 10


class IrQwebAuditfileStringWidget15(models.AbstractModel):
    _name = 'ir.qweb.field.auditfile.string15'
    _inherit = 'ir.qweb.field.auditfile.string999'
    _max_length = 15


class IrQwebAuditfileStringWidget20(models.AbstractModel):
    _name = 'ir.qweb.field.auditfile.string20'
    _inherit = 'ir.qweb.field.auditfile.string999'
    _max_length = 20


class IrQwebAuditfileStringWidget30(models.AbstractModel):
    _name = 'ir.qweb.field.auditfile.string30'
    _inherit = 'ir.qweb.field.auditfile.string999'
    _max_length = 30


class IrQwebAuditfileStringWidget50(models.AbstractModel):
    _name = 'ir.qweb.field.auditfile.string50'
    _inherit = 'ir.qweb.field.auditfile.string999'
    _max_length = 50
