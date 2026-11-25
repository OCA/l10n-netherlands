# Copyright 2024 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    liza_login = fields.Char(related="company_id.liza_login", readonly=False)
    liza_password = fields.Char(related="company_id.liza_password", readonly=False)
    liza_followup_enable = fields.Boolean(
        related="company_id.liza_followup_enable", readonly=False
    )
    fill_liza_name = fields.Boolean(related="company_id.fill_liza_name", readonly=False)
    fill_liza_commercial_name = fields.Boolean(
        related="company_id.fill_liza_commercial_name", readonly=False
    )
    fill_liza_street = fields.Boolean(
        related="company_id.fill_liza_street", readonly=False
    )
    fill_liza_zip = fields.Boolean(related="company_id.fill_liza_zip", readonly=False)
    fill_liza_city = fields.Boolean(related="company_id.fill_liza_city", readonly=False)
    fill_liza_country_id = fields.Boolean(
        related="company_id.fill_liza_country_id", readonly=False
    )
    fill_liza_email = fields.Boolean(
        related="company_id.fill_liza_email", readonly=False
    )
    fill_liza_website = fields.Boolean(
        related="company_id.fill_liza_website", readonly=False
    )
    fill_liza_phone = fields.Boolean(
        related="company_id.fill_liza_phone", readonly=False
    )
    fill_liza_vat = fields.Boolean(related="company_id.fill_liza_vat", readonly=False)
    fill_liza_registry = fields.Boolean(
        related="company_id.fill_liza_registry", readonly=False
    )
