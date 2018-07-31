# Copyright 2013-2015 Therp BV <https://therp.nl>
# @autors: Stefan Rijnhart, Ronald Portier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.tools import ormcache


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    @ormcache(skiparg=2)
    def get_provider_obj(self):
        apikey = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_nl_postcodeapi.apikey', '').strip()
        if not apikey or apikey == 'Your API key':
            return False
        from pyPostcode import Api
        return Api(apikey, (2, 0, 0))

    def _postcodeapi_check_valid_provider(self, provider):
        test = provider.getaddress('1053NJ', '334T')
        if not test or not test._data:
            return _('Could not verify the connection with the address '
                     'lookup service (if you want to get rid of this '
                     'message, please rename or delete the system parameter '
                     '\'l10n_nl_postcodeapi.apikey\').')
        return None

    @api.model
    @ormcache(skiparg=2)
    def get_province(self, province):
        """ Return the province or empty recordset """
        if not province:
            return self.env['res.country.state']
        return self.env['res.country.state'].search([
            ('name', '=', province)
        ], limit=1)

    @api.onchange('zip', 'street_number', 'country_id')
    def on_change_zip_street_number(self):
        """
        Normalize the zip code, check on the partner's country and
        if all is well, request address autocompletion data.

        NB. postal_code is named 'zip' in Odoo, but is this a reserved
        keyword in Python
        """
        postal_code = self.zip and self.zip.replace(' ', '')
        country = self.country_id
        if not (postal_code and self.street_number) or \
                country and country != self.env.ref('base.nl'):
            return {}

        provider_obj = self.get_provider_obj()
        if not provider_obj:
            return {}
        err_msg = self._postcodeapi_check_valid_provider(provider_obj)
        if err_msg:
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': err_msg,
                }
            }
        pc_info = provider_obj.getaddress(postal_code, self.street_number)
        if not pc_info or not pc_info._data:
            return {}
        self.street_name = pc_info.street
        self.city = pc_info.town
        self.state_id = self.get_province(pc_info.province)
