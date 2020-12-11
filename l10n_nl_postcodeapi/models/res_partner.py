# Copyright 2013-2020 Therp BV <https://therp.nl>
# @autors: Stefan Rijnhart, Ronald Portier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)
try:
    import pyPostcode
except ImportError as err:  # pragma: no cover
    _logger.debug(err)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def get_provider_obj(self):
        apikey = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_nl_postcodeapi.apikey', '').strip()
        if not apikey or apikey == 'Your API key':
            return False
        return pyPostcode.Api(apikey, (3, 0, 0))

    @api.model
    def get_province(self, province):
        """ Return the province or empty recordset """
        if not province:
            return self.env['res.country.state']
        return self.env['res.country.state'].search([
            ('name', '=', province)
        ], limit=1)

    @api.onchange('zip', 'street_number', 'country_id')
    def onchange_zip_l10n_nl_postcode(self):
        """
        Normalize the zip code, check on the partner's country and
        if all is well, request address autocompletion data.

        NB. postal_code is named 'zip' in Odoo, but is this a reserved
        keyword in Python
        """
        if not self._l10n_nl_do_check_postcode():
            return {}
        result = super().onchange_zip_l10n_nl_postcode()
        # Do not check postcode if we already know it is not valid.
        if result and "warning" in result:
            return result
        # Only check when we have a postal code and a street_number:
        postal_code = self.zip and self.zip.replace(' ', '')
        if not postal_code and self.street_number:
            return result
        provider_obj = self.get_provider_obj()
        if not provider_obj:
            return result
        pc_info = provider_obj.getaddress(postal_code, self.street_number)
        if pc_info and pc_info._data:
            self.street_name = pc_info.street
            self.city = pc_info.city
            self.state_id = self.get_province(pc_info.province)
        else:
            result['warning'] = self._l10n_nl_postcode_get_warning(
                _(
                    "Cannot validate postalcode (%s),"
                    " or postal code invalid for housenumber"
                )
            )
        return result
