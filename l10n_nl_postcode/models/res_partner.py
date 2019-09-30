# Copyright 2016-2020 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)
try:
    from stdnum.nl import postcode
except ImportError:
    _logger.debug("Cannot import stdnum.nl.postcode.")


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _l10n_nl_postcode_get_warning(self):
        self.ensure_one()
        msg = _("The Postcode you entered (%s) is not valid.")
        return {"title": _("Warning!"), "message": msg % self.zip}

    def _l10n_nl_postcode_check_country(self):
        self.ensure_one()
        if not self.country_id or self.country_id != self.env.ref("base.nl"):
            return False
        return True

    @api.onchange("zip", "country_id")
    def onchange_zip_l10n_nl_postcode(self):
        # if 'skip_postcode_check' passed in context: will disable the check
        if self.env.context.get("skip_postcode_check"):
            return

        if self.zip and self._l10n_nl_postcode_check_country():
            # check that the postcode is valid
            if postcode.is_valid(self.zip):
                # properly format the entered postcode
                self.zip = postcode.validate(self.zip)
            else:
                # display a warning
                warning_msg = self._l10n_nl_postcode_get_warning()
                return {"warning": warning_msg}
