# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
from openerp.osv import orm
from openerp.tools import ormcache
from openerp.tools.translate import _
from ..extra_packages.pyPostcode import Api as pyPostcodeApi


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    @ormcache(skiparg=2)
    def get_provider_obj(self, cr):
        cr.execute("""
                SELECT value FROM ir_config_parameter
                WHERE key = %s""", ('l10n_nl_postcodeapi.apikey',))
        row = cr.fetchone()
        if row and row[0] != 'Your API key' and row[0].strip():
            provider = pyPostcodeApi(row[0].strip())
            test = provider.getaddress('1053NJ', '334T')
            if not test or not test._data:
                raise orm.except_orm(
                    _('Error'),
                    _('Could not verify the connection with the address '
                      'lookup service (if you want to get rid of this '
                      'message, please rename or delete the system parameter '
                      '\'l10n_nl_postcodeapi.apikey\').'))
            return provider
        return False

    @ormcache(skiparg=3)
    def get_country_nl(self, cr, uid):
        data_obj = self.pool.get('ir.model.data')
        try:
            return data_obj.get_object_reference(cr, uid, 'base', 'nl')[1]
        except ValueError:
            return False

    @ormcache(skiparg=3)
    def get_province(self, cr, uid, province):
        if not province:
            return False
        res = self.pool.get('res.country.state').search(
            cr, uid, [('name', '=', province)])
        return res[0] if res else False

    def on_change_zip_street_number(
            self, cr, uid, ids, postal_code,
            street_number, country_id, context=None):
        """
        Normalize the zip code, check on the partner's country and
        if all is well, request address autocompletion data.

        NB. postal_code is named 'zip' in OpenERP, but is this a reserved
        keyword in Python
        """
        postal_code = postal_code and postal_code.replace(' ', '')
        if not (postal_code and street_number):
            return {}

        if country_id:
            if country_id != self.get_country_nl(cr, uid):
                return {}
        provider_obj = self.get_provider_obj(cr)
        if not provider_obj:
            return {}
        pc_info = provider_obj.getaddress(
            postal_code, street_number)
        if not pc_info or not pc_info._data:
            return {}
        return {'value': {
                'street_name': pc_info._data['street'],
                'city': pc_info._data['town'],
                'state_id': self.get_province(cr, uid, pc_info._province),
                }}

    def fields_view_get(
            self, cr, user, view_id=None, view_type='form',
            context=None, toolbar=False, submenu=False):
        """ Address fields can be all over the place due to module
        interaction. For improved compatibility add the onchange method here,
        not in a view."""
        res = super(ResPartner, self).fields_view_get(
            cr, user, view_id=view_id, view_type=view_type,
            context=context, toolbar=toolbar, submenu=submenu)
        if view_type != 'form':
            return res

        def inject_onchange(arch):
            arch = etree.fromstring(arch)
            for field in ['zip', 'street_number']:
                count = 0
                for node in arch.xpath('//field[@name="%s"]' % field):
                    count += 1
                    node.attrib['on_change'] = (
                        "on_change_zip_street_number"
                        "(zip, street_number, country_id, context)")
            return etree.tostring(arch, encoding='utf-8')

        res['arch'] = inject_onchange(res['arch'])
        # Inject in the embedded contacts view as well
        if res['fields'].get('child_ids', {}).get('views', {}).get('form'):
            res['fields']['child_ids']['views']['form']['arch'] = \
                inject_onchange(
                    res['fields']['child_ids']['views']['form']['arch'])
        return res
