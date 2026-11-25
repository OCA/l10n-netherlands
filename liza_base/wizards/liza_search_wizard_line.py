# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LizaBaseSearchWizardLine(models.TransientModel):
    _name = "liza.search.wizard.line"
    _description = "Liza Search Wizard Line"

    wizard_id = fields.Many2one("liza.search.wizard", required=True, ondelete="cascade")

    name = fields.Char()
    street = fields.Char()
    city = fields.Char()
    country = fields.Char()
    country_code = fields.Char()
    registry = fields.Char()
    is_active = fields.Boolean("Active")

    def select(self):
        self.ensure_one()
        country = self.env["res.country"].search([("code", "=", self.country_code)])
        self.wizard_id.partner_id.write(
            {
                "company_registry": self.registry,
                "country_id": country.id,
            }
        )
        self.wizard_id.partner_id._liza_enhance()
        self.wizard_id.partner_id.liza_button_copy_address()
