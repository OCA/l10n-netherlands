# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import models


class L10nNlVatStatement(models.Model):
    _inherit = "l10n.nl.vat.statement"

    def _create_icp_lines(self):
        # do nothing if called from a vat statement
        if self._name == "l10n.nl.vat.statement":
            return
        return super()._create_icp_lines()
