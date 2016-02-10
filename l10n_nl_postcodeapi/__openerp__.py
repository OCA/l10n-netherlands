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
    'summary': 'Autocomplete Dutch addresses using PostcodeApi.nu',
    'description': '''

Auto-completion for Dutch addresses
===================================
This module contains integration of the excellent and free address completion
service 'PostcodeAPI'. The service allows lookups by zip code and house number,
providing street name and city. The lookups will be triggered in the partner
form views when a zip code or house number is entered or modified. Only
Dutch addresses (which is assumed to include addresses with no country) are
auto-completed.

More info about the lookup service here: http://www.postcodeapi.nu/

Dependencies
============
This module depends on the module partner_street_number, which will split
up the street field into separate fields for street name and number.

You also need to have the 'pyPostcode' Python library by Stefan Jansen
installed (https://github.com/steffex/pyPostcode). Install in the following way
for now, until this lib is available on Pypi::

    pip install git+https://github.com/stefanrijnhart/pyPostcode.git@pypi

Configuration
=============
Please enter the API key that you request from PostcodeAPI into the system
parameter 'l10n_nl_postcodeapi.apikey'

Provinces are autocompleted if a country state with the exact name is found in
the system. A CSV file with the Dutch provinces is included in the data
directory, but not loaded by default. You can import the file manually.

Compatibility
=============
This module is compatible with OpenERP 7.0.
''',
    'version': '0.1',
    'author': 'Therp BV',
    'category': 'Localization',
    'website': 'https://github.com/OCA/l10n-netherlands',
    'license': 'AGPL-3',
    'depends': ['partner_street_number'],
    'data': [
        'data/ir_config_parameter.xml',
        ],
    "external_dependencies": {
        'python': ['pyPostcode'],
    }
}
