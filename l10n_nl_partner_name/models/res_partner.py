# Copyright 2017-2022 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResPartner(models.Model):
    """Extend res.partner with extra fields for Dutch names."""

    _inherit = "res.partner"

    initials = fields.Char()
    infix = fields.Char()

    @api.depends("firstname", "lastname", "initials", "infix")
    def _compute_name(self):
        for record in self:
            record.name = record._get_computed_name(
                record.lastname, record.firstname, record.initials, record.infix
            )
