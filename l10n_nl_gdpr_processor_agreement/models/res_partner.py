# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    data_protection_officer_id = fields.Many2one(
        'res.partner', compute='_compute_data_protection_officer_id',
    )

    @api.multi
    def _compute_data_protection_officer_id(self):
        for this in self:
            this.data_protection_officer_id = this.child_ids.filtered(
                lambda x: x.category_id & self.env.ref(
                    'l10n_nl_gdpr_processor_agreement.'
                    'res_partner_category_data_protection_officer'
                )
            )[:1] or this.child_ids[:1] or this
