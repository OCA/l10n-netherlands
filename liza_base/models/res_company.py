# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    liza_login = fields.Char(groups="liza_base.liza_download")
    liza_password = fields.Char(groups="liza_base.liza_download")
    liza_followup_enable = fields.Boolean("Enable Contact Data Followup")

    fill_liza_name = fields.Boolean(default=True)
    fill_liza_commercial_name = fields.Boolean(default=True)
    fill_liza_street = fields.Boolean(default=True)
    fill_liza_zip = fields.Boolean(default=True)
    fill_liza_city = fields.Boolean(default=True)
    fill_liza_country_id = fields.Boolean(default=True)
    fill_liza_email = fields.Boolean(default=True)
    fill_liza_website = fields.Boolean(default=True)
    fill_liza_phone = fields.Boolean(default=True)
    fill_liza_vat = fields.Boolean(default=True)
    fill_liza_registry = fields.Boolean(default=True)

    _liza_login_unique = models.Constraint(
        "UNIQUE(liza_login)",
        "These credentials are already in use, please contact Liza.",
    )
