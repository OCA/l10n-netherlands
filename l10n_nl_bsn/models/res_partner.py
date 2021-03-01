# Copyright 2016-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)
try:
    from stdnum.nl import bsn
except ImportError:
    _logger.debug("Cannot `import stdnum.nl.bsn`.")


class ResPartner(models.Model):
    _inherit = "res.partner"

    bsn_number = fields.Char(string="BSN", groups="hr.group_hr_user")

    @api.onchange("bsn_number")
    def onchange_bsn_number(self):
        warning = {}
        if self.bsn_number:
            # properly format the entered BSN
            self.bsn_number = bsn.format(self.bsn_number)

            # check is valid, otherwise display a warning
            warning = self._warn_bsn_invalid()

            # search for another partner with the same BSN
            args = [("bsn_number", "=", self.bsn_number), ("name", "!=", self.name)]

            # refine search in case of multicompany setting
            if self.company_id:
                args += [("company_id", "=", self.company_id.id)]
            other_partner = self.search(args, limit=1)

            # if another partner exists, display a warning
            if other_partner:
                warning = other_partner._warn_bsn_existing()
        return {"warning": warning}

    def _warn_bsn_invalid(self):
        self.ensure_one()
        warning = {}
        if not bsn.is_valid(self.bsn_number):
            msg = _("The BSN you entered (%s) is not valid.")
            warning = {"title": _("Warning!"), "message": msg % self.bsn_number}
        return warning

    def _warn_bsn_existing(self):
        self.ensure_one()
        msg = _("Another person (%s) has the same BSN (%s).")
        warning = {
            "title": _("Warning!"),
            "message": msg % (self.name, self.bsn_number),
        }
        return warning

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        res_domain = []
        for domain in args:
            if (
                len(domain) > 2
                and domain[0] == "bsn_number"
                and isinstance(domain[2], str)
                and domain[2]
                and domain[1] not in expression.NEGATIVE_TERM_OPERATORS
                and not self.env.context.get("skip_formatted_bsn_number_search")
            ):
                operator = domain[1]
                bsn_number = domain[2]
                bsn_compact = bsn.compact(bsn_number)
                bsn_domain = expression.OR(
                    [
                        [("bsn_number", operator, bsn_number)],
                        [("bsn_number", operator, bsn_compact)],
                    ]
                )
                if bsn.is_valid(bsn_number):
                    bsn_format = bsn.format(bsn_number)
                    bsn_domain = expression.OR(
                        [bsn_domain, [("bsn_number", operator, bsn_format)]]
                    )
                res_domain += bsn_domain
            else:
                res_domain.append(domain)
        return super().search(
            res_domain, offset=offset, limit=limit, order=order, count=count
        )
