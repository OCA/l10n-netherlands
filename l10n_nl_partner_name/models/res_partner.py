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

    def _inverse_name(self):
        for record in self:
            parts = record._get_inverse_name(record.name, record.is_company)
            record.update(parts)

    @api.model
    def _get_computed_name(self, lastname, firstname, initials=None, infix=None):
        return " ".join(
            filter(
                None,
                (firstname, ("(%s)" % initials) if initials else None, infix, lastname),
            )
        )

    @api.model
    def _get_inverse_name(self, name, is_company=False):
        if is_company:
            return super()._get_inverse_name(name, is_company=is_company)

        def add_token(key, value):
            result[key] += (result[key] and " " or "") + value

        infixes = self._l10n_nl_partner_name_infixes()
        result = dict.fromkeys(("firstname", "lastname", "initials", "infix"), "")
        tokens = (name or "").split()
        while len(tokens) > 1:
            token = tokens.pop(0)
            if all((c.isupper() or c == ".") for c in token):
                add_token("initials", token)
            elif token[:1] == "(" and token[-1:] == ")":
                add_token("initials", token[1:-1])
            elif (
                len(tokens) and " ".join([token.lower(), tokens[0].lower()]) in infixes
            ):
                add_token("infix", " ".join([token.lower(), tokens[0].lower()]))
                tokens.pop(0)
            elif token.lower() in infixes:
                add_token("infix", token)
            elif result["infix"]:
                tokens.insert(0, token)
                break
            else:
                add_token("firstname", token)
        result["lastname"] = " ".join(tokens)
        return result

    def _l10n_nl_partner_name_infixes(self):
        return tuple(
            map(
                str.strip,
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "l10n_nl_partner_name_infixes", "van,der,den,op,ter,de,v/d,d','t,te"
                )
                .split(","),
            )
        )
