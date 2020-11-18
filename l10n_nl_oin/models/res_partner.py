# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    nl_oin = fields.Char(
        "Dutch OIN", copy=False, help="Dutch Organisatie-identificatienummer (OIN)"
    )
    nl_oin_display = fields.Boolean(compute="_compute_nl_oin_display")

    @api.depends("country_id", "is_company")
    def _compute_nl_oin_display(self):
        for partner in self:
            if not partner.is_company:
                partner.nl_oin_display = False
            elif partner.country_id != self.env.ref("base.nl"):
                partner.nl_oin_display = False
            else:
                partner.nl_oin_display = True

    @api.onchange("nl_oin")
    def onchange_nl_oin(self):
        warning = {}
        if self.nl_oin:
            # check is valid, otherwise display a warning
            warning = self._warn_oin_invalid()

            # search for another partner with the same OIN
            args = [("nl_oin", "=", self.nl_oin), ("name", "!=", self.name)]

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
        if len(self.nl_oin) != 20 or not self.nl_oin.isdigit():
            msg = _("The OIN you entered (%s) is not valid.")
            warning = {"title": _("Warning!"), "message": msg % self.nl_oin}
        return warning

    def _warn_oin_existing(self):
        self.ensure_one()
        msg = _("Another partner (%s) has the same OIN (%s).")
        warning = {
            "title": _("Warning!"),
            "message": msg % (self.name, self.nl_oin),
        }
        return warning
