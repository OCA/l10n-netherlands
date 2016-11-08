# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013-2015 Therp BV (<http://therp.nl>).
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

{
    'name': 'Integration with PostcodeApi.nu',
    'images': [],
    'summary': 'Autocomplete Dutch addresses using PostcodeApi.nu',
    'version': '10.0.0.1.0',
    'author': 'Therp BV,Odoo Community Association (OCA)',
    'category': 'Localization',
    'website': 'https://github.com/OCA/l10n-netherlands',
    'license': 'AGPL-3',
    'depends': ['partner_street_number'],
    'data': [
        'data/ir_config_parameter.xml',
        ],
    'external_dependencies': {
        'python': ['pyPostcode'],
    },
    'installable': True,
}
