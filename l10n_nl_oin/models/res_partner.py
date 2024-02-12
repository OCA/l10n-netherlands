# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_nl_oin = fields.Char(
        copy=False, help="Dutch Organisatie-identificatienummer (OIN)"
    )

    @api.onchange("l10n_nl_oin")
    def onchange_nl_oin(self):
        warning = {}
        if self.l10n_nl_oin:
            # check is valid, otherwise display a warning
            warning = self._warn_oin_invalid()

            # search for another partner with the same OIN
            args = [("l10n_nl_oin", "=", self.l10n_nl_oin), ("name", "!=", self.name)]

            # refine search in case of multicompany setting
            if self.company_id:
                args += [("company_id", "=", self.company_id.id)]
            other_partner = self.search(args, limit=1)

            # if another partner exists, display a warning
            if other_partner:
                warning = other_partner._warn_oin_existing()
        return {"warning": warning}

    def _warn_oin_invalid(self):
        self.ensure_one()
        warning = {}
        if len(self.l10n_nl_oin) != 20 or not self.l10n_nl_oin.isdigit():
            msg = _("The OIN you entered (%(oin)s) is not valid.")
            warning = {
                "title": _("Warning!"),
                "message": msg % {"oin": self.l10n_nl_oin},
            }
        return warning

    def _warn_oin_existing(self):
        self.ensure_one()
        msg = _("Another partner (%(name)s) has the same OIN (%(oin)s).")
        warning = {
            "title": _("Warning!"),
            "message": msg % {"name": self.name, "oin": self.l10n_nl_oin},
        }
        return warning
