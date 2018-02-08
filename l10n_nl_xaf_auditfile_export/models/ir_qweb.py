# -*- coding: utf-8 -*-
# Copyright (C) 2015 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class IrQwebAuditfileStringWidget999(models.AbstractModel):
    _name = 'ir.qweb.widget.auditfile.string999'
    _inherit = 'ir.qweb.widget'
    _max_length = 999

    def _trunk_eval(self, expr, qwebcontext):
        if expr == "0":
            return qwebcontext.get(0, '')
        val = self.pool['ir.qweb'].eval(expr, qwebcontext)
        if isinstance(val, basestring):
            val = val[:self._max_length]
        if isinstance(val, unicode):
            return val.encode("utf8")
        if val is False or val is None:
            return ''
        return str(val)

    def _format(self, inner, options, qwebcontext):
        return self._trunk_eval(inner, qwebcontext)


class IrQwebAuditfileStringWidget9(models.AbstractModel):
    _name = 'ir.qweb.widget.auditfile.string9'
    _inherit = 'ir.qweb.widget.auditfile.string999'
    _max_length = 9


class IrQwebAuditfileStringWidget10(models.AbstractModel):
    _name = 'ir.qweb.widget.auditfile.string10'
    _inherit = 'ir.qweb.widget.auditfile.string999'
    _max_length = 10


class IrQwebAuditfileStringWidget15(models.AbstractModel):
    _name = 'ir.qweb.widget.auditfile.string15'
    _inherit = 'ir.qweb.widget.auditfile.string999'
    _max_length = 15


class IrQwebAuditfileStringWidget20(models.AbstractModel):
    _name = 'ir.qweb.widget.auditfile.string20'
    _inherit = 'ir.qweb.widget.auditfile.string999'
    _max_length = 20


class IrQwebAuditfileStringWidget30(models.AbstractModel):
    _name = 'ir.qweb.widget.auditfile.string30'
    _inherit = 'ir.qweb.widget.auditfile.string999'
    _max_length = 30


class IrQwebAuditfileStringWidget50(models.AbstractModel):
    _name = 'ir.qweb.widget.auditfile.string50'
    _inherit = 'ir.qweb.widget.auditfile.string999'
    _max_length = 50
