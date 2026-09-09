# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    liza_payment_info_enable = fields.Boolean(
        related="company_id.liza_payment_info_enable",
        readonly=False,
    )
