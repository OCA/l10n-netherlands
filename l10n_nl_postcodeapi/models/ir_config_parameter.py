# Copyright 2013-2021 Therp BV <https://therp.nl>
# @autors: Stefan Rijnhart, Ronald Portier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Interface to the configured (or not) Postcode API."""
# pylint: disable=protected-access
try:
    import pyPostcode
except ImportError:
    pyPostcode = None

from odoo.exceptions import UserError
from odoo import api, models, _
from odoo.tools import ormcache


class IrConfigParameter(models.Model):
    """Interface to the configured (or not) Postcode API."""
    _inherit = 'ir.config_parameter'

    @api.model
    @ormcache(skiparg=2)
    def get_provider_obj(self):
        """get Api to interface with Dutch postcode provider."""
        if not pyPostcode:
            # Module not loaded.
            return None  # pragma: no cover
        apikey = self.sudo().get_param('l10n_nl_postcodeapi.apikey', '').strip()
        if not apikey or apikey == 'Your API key':
            return None
        provider_obj = pyPostcode.Api(apikey, (2, 0, 0))
        test = provider_obj.getaddress('1053NJ', '334T')
        if not test or not test._data:
            raise UserError(_(
                'Could not verify the connection with the address lookup service'
                ' (if you want to get rid of this message, please rename or delete'
                ' the system parameter \'l10n_nl_postcodeapi.apikey\').'
            ))
        return provider_obj

    @api.model
    def create(self, vals):
        """Clear the postcode provider cache when the API key is created."""
        new_record = super().create(vals)
        new_record._check_and_reset_provider()
        return new_record

    @api.multi
    def write(self, vals):
        """Clear the postcode provider cache when the API key is modified."""
        result = super().write(vals)
        self._check_and_reset_provider()
        return result

    def _check_and_reset_provider(self):
        """Clear provider cache and check wether key valid."""
        for this in self:
            if this.key == 'l10n_nl_postcodeapi.apikey':
                this.get_provider_obj.clear_cache(this)
                this.get_provider_obj()
