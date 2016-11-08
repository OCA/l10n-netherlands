# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013-2015 Therp BV (<http://therp.nl>).
#
#    @autors: Stefan Rijnhart, Ronald Portier
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from lxml import etree
from odoo import models, api, exceptions, _
from odoo.tools import ormcache


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    @ormcache(skiparg=2)
    def get_provider_obj(self):
        apikey = self.env['ir.config_parameter'].get_param(
            'l10n_nl_postcodeapi.apikey', '').strip()
        if not apikey or apikey == 'Your API key':
            return False
        from pyPostcode import Api
        provider = Api(apikey, (2, 0, 0))
        test = provider.getaddress('1053NJ', '334T')
        if not test or not test._data:
            raise exceptions.Warning(
                _('Error'),
                _('Could not verify the connection with the address '
                  'lookup service (if you want to get rid of this '
                  'message, please rename or delete the system parameter '
                  '\'l10n_nl_postcodeapi.apikey\').'))
        return provider

    @api.model
    @ormcache(skiparg=2)
    def get_province(self, province):
        """ Return the province or empty recordset """
        if not province:
            return self.env['res.country.state']
        res = self.env['res.country.state'].search([('name', '=', province)])
        return res[0] if res else res

    @api.onchange('zip', 'street_number', 'country_id')
    def on_change_zip_street_number(self):
        """
        Normalize the zip code, check on the partner's country and
        if all is well, request address autocompletion data.

        NB. postal_code is named 'zip' in OpenERP, but is this a reserved
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
        pc_info = provider_obj.getaddress(postal_code, self.street_number)
        if not pc_info or not pc_info._data:
            return {}
        self.street_name = pc_info.street
        self.city = pc_info.town
        self.state_id = self.get_province(pc_info.province)

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form',
            toolbar=False, submenu=False):
        """ Address fields can be all over the place due to module
        interaction. For improved compatibility add the onchange method here,
        not in a view."""
        res = super(ResPartner, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        if view_type != 'form':
            return res

        def inject_onchange(arch):
            arch = etree.fromstring(arch)
            for field in ['zip', 'street_number', 'country_id']:
                for node in arch.xpath('//field[@name="%s"]' % field):
                    node.attrib['on_change'] = "1"
            return etree.tostring(arch, encoding='utf-8')

        res['arch'] = inject_onchange(res['arch'])
        # Inject in the embedded contacts view as well
        if res['fields'].get('child_ids', {}).get('views', {}).get('form'):
            res['fields']['child_ids']['views']['form']['arch'] = \
                inject_onchange(
                    res['fields']['child_ids']['views']['form']['arch'])
        return res
