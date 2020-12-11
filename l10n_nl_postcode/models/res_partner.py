# Copyright 2016-2018 Onestein (<http://www.onestein.eu>)
# Copyright 2020 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)
try:
    from stdnum.nl import postcode
except ImportError:
    _logger.debug('Cannot import stdnum.nl.postcode.')


class ResPartner(models.Model):
    """Add functions to check dutch postcode."""
    _inherit = 'res.partner'

    @api.multi
    def _l10n_nl_postcode_get_warning(self, message):
        """Utility to set warning message for onchange methods."""
        self.ensure_one()
        warning = {
            'title': _('Warning!'),
            'message': message % self.zip,
        }
        return warning

    @api.multi
    def _l10n_nl_do_check_postcode(self):
        """Only check postcode for Dutch addresses and when not disabled in context."""
        self.ensure_one()
        # if 'skip_postcode_check' passed in context: will disable the check
        if self.env.context.get('skip_postcode_check'):
            return False
        # If not explicitly in the Netherlands do not check:
        if not self.country_id or self.country_id != self.env.ref('base.nl'):
            return False
        return True

    @api.onchange('zip', 'country_id')
    def onchange_zip_l10n_nl_postcode(self):
        """Check postcode if country is or becomes Netherlands and field has value."""
        result = {}
        if not self._l10n_nl_do_check_postcode():
            return result
        # check that the postcode is valid
        if postcode.is_valid(self.zip):
            # properly format the entered postcode
            self.zip = postcode.validate(self.zip)
        else:
            # display a warning
            result['warning'] = self._l10n_nl_postcode_get_warning(
                _('The Postcode you entered (%s) is not valid.')
            )
        return result
