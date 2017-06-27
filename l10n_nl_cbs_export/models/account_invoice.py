# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    cbs_export_id = fields.Many2one('cbs.export.file', 'CBS Export')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
