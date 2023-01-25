# Copyright 2023 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class VatStatement(models.Model):
    _inherit = "l10n.nl.vat.statement"

    date_range_id = fields.Many2one("date.range", "Date range")

    @api.onchange("date_range_id")
    def onchange_date_range_id(self):
        if self.date_range_id and self.state == "draft":
            self.update(
                {
                    "from_date": self.date_range_id.date_start,
                    "to_date": self.date_range_id.date_end,
                }
            )
