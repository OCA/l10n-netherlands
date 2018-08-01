# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV <http://therp.nl>.
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
    "name": "XAF auditfile export",
    "version": "10.0.1.0.2",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "summary": "Export XAF auditfiles for Dutch tax authorities",
    "depends": [
        "base",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/xaf_auditfile_export.xml",
        "views/templates.xml",
        "views/menu.xml",
    ],
    "installable": True,
}
