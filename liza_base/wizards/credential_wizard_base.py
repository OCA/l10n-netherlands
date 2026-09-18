# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class LizaCredentialWizardBase(models.TransientModel):
    _name = "liza_base.credential_wizard_base"
    _description = "Ask for Liza login & password"
    _inherit = ["liza_base.credential_wizard_abstract"]

    def _return_action(self):
        return (
            self.env["res.partner"]
            .browse(self.env.context["active_id"])
            .liza_button_enhance()
        )
