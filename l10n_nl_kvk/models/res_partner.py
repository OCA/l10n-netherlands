# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_not_nl_company = fields.Boolean(compute='_compute_is_not_nl_company')

    @api.depends('country_id')
    def _compute_is_not_nl_company(self):
        for partner in self:
            partner.is_not_nl_company = False
            country = partner.country_id
            if country and country != self.env.ref('base.nl'):
                partner.is_not_nl_company = True

    def load_partner_values_from_kvk(self):
        self.ensure_one()

        if self.is_not_nl_company:
            return

        kvk = self.coc_registration_number
        if not kvk:
            raise UserError(_(
                "KvK not set.\n"
                "Please enter a KvK first."))

        wizard = self.env['l10n.nl.kvk.preview.wizard'].create({
            'partner_id': self.id,
            'kvk': kvk,
        })

        if not wizard.line_ids:
            raise UserError(_(
                "No record found for this KvK.\n"
                "Please enter a valid KvK number."))

        return wizard.action_load_partner_values()

    def load_partner_values_from_name(self):
        self.ensure_one()

        if self.is_not_nl_company:
            return

        wizard = self.env['l10n.nl.kvk.preview.wizard'].create({
            'partner_id': self.id,
            'name': self.name,
        })

        if not wizard.line_ids:
            raise UserError(_(
                "No record found for this name.\n"
                "Please enter a valid partner name."))

        return wizard.action_load_partner_values()
