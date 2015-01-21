# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
    "name": "Dutch partner names",
    "version": "1.0",
    "author": "Therp BV",
    "complexity": "normal",
    "description": """Use Dutch conventions for partner names:
    - have infixes
    - have initials
    - split first and last name (provided by partner_firstname)
    - use a different title for address and salutation ('aan de heer'/'geachte
      heer')
    """,
    "category": "Generic Modules",
    "depends": [
        'partner_firstname',
    ],
    "data": [
        'data/migration.xml',
        "data/res_partner_title.xml",
        "view/res_partner_title.xml",
        'view/res_partner.xml',
    ],
    "js": [
    ],
    "css": [
    ],
    "qweb": [
    ],
    "auto_install": False,
    "installable": True,
    "external_dependencies": {
        'python': ['mako'],
    },
}
