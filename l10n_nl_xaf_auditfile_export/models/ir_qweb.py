# Copyright 2015 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrQwebAuditfileStringWidget999(models.AbstractModel):
    _name = "ir.qweb.field.auditfile.string999"
    _description = "ir.qweb.field.auditfile.string999"
    _inherit = "ir.qweb.field"
    _max_length = 999

    @api.model
    def value_to_html(self, value, options):
        value = value[: self._max_length] if value else ""
        return super().value_to_html(value, options)


class IrQwebAuditfileStringWidget9(models.AbstractModel):
    _name = "ir.qweb.field.auditfile.string9"
    _description = "ir.qweb.field.auditfile.string9"
    _inherit = "ir.qweb.field.auditfile.string999"
    _max_length = 9


class IrQwebAuditfileStringWidget10(models.AbstractModel):
    _name = "ir.qweb.field.auditfile.string10"
    _description = "ir.qweb.field.auditfile.string10"
    _inherit = "ir.qweb.field.auditfile.string999"
    _max_length = 10


class IrQwebAuditfileStringWidget15(models.AbstractModel):
    _name = "ir.qweb.field.auditfile.string15"
    _description = "ir.qweb.field.auditfile.string15"
    _inherit = "ir.qweb.field.auditfile.string999"
    _max_length = 15


class IrQwebAuditfileStringWidget20(models.AbstractModel):
    _name = "ir.qweb.field.auditfile.string20"
    _description = "ir.qweb.field.auditfile.string20"
    _inherit = "ir.qweb.field.auditfile.string999"
    _max_length = 20


class IrQwebAuditfileStringWidget30(models.AbstractModel):
    _name = "ir.qweb.field.auditfile.string30"
    _description = "ir.qweb.field.auditfile.string30"
    _inherit = "ir.qweb.field.auditfile.string999"
    _max_length = 30


class IrQwebAuditfileStringWidget35(models.AbstractModel):
    _name = "ir.qweb.field.auditfile.string35"
    _description = "ir.qweb.field.auditfile.string35"
    _inherit = "ir.qweb.field.auditfile.string999"
    _max_length = 35


class IrQwebAuditfileStringWidget50(models.AbstractModel):
    _name = "ir.qweb.field.auditfile.string50"
    _description = "ir.qweb.field.auditfile.string50"
    _inherit = "ir.qweb.field.auditfile.string999"
    _max_length = 50
