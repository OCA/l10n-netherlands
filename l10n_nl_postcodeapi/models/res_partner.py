# Copyright 2013-2021 Therp BV <https://therp.nl>
# @autors: Stefan Rijnhart, Ronald Portier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Interface with Dutch Postcode API service."""
# pylint: disable=protected-access
import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Interface with Dutch Postcode API service."""
    _inherit = 'res.partner'

    @api.model
    def get_country_state(self, country, state_name):
        """Lookup state within a country."""
        state_model = self.env['res.country.state']
        if not country or not state_name:
            return state_model
        return state_model.search(
            [
                ('country_id', '=', country.id),
                ('name', '=', state_name),
            ],
            limit=1
        )

    @api.onchange('zip', 'street_number', 'country_id')
    def on_change_zip_street_number(self):
        """Autocomplete dutch addresses if postalcode and streetnumber are filled.

        NB. postal_code is named 'zip' in Odoo, but is this a reserved
        keyword in Python.
        """
        country_nl = self.env.ref('base.nl')
        country = self.country_id
        if country and country != country_nl:
            # Do not check for postal code outside of the Netherlands.
            return
        postal_code = self.zip and self.zip.replace(' ', '')
        if not postal_code or not self.street_number:
            # Only check if both postal code and street number have been filled.
            return
        parameter_model = self.env["ir.config_parameter"]
        provider_obj = parameter_model.get_provider_obj()
        if not provider_obj:
            # Do not check when we can not use API.
            return  # pragma: no cover
        pc_info = provider_obj.getaddress(postal_code, self.street_number)
        if not pc_info or not pc_info._data:  # pragma: no cover
            # Should not really happen in the Netherlands.
            _logger.warning(
                _(
                    "No address found for partner %s, with postalcode %s and"
                    " housenumber %d."
                ),
                self.display_name,
                postal_code,
                self.street_number
            )
            return
        vals = {
            "street_name": pc_info.street,
            "city": pc_info.town,
            "state_id": self.get_country_state(country_nl, pc_info.province).id
        }
        self.update(vals)
