# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class LizaCredentialWizardAbstract(models.AbstractModel):
    _name = "liza_base.credential_wizard_abstract"
    _description = "Ask for Liza login & password"

    liza_login = fields.Char("Login", required=True)
    liza_password = fields.Char("Password", required=True)

    def _return_action(self):
        return True

    def save_liza_login_pwd(self):
        """
        save information given in the form to the logged-in user
        """
        self.ensure_one()
        company_sudo = self.env.company.sudo()
        company_sudo.liza_login = self.liza_login
        company_sudo.liza_password = self.liza_password
        return self._return_action()
