# -*- encoding: utf-8 -*-
##############################################################################
#
#    XAF Auditfile export
#    Copyright (C) 2014 ONESTEiN BV (<http://www.onestein.nl>).
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
    'name': 'XAF Auditfile Export',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    'complexity': "normal",
    'description': """
XAF Auditfile Export
===============================

This module allows to export the financial (accounting) information
from your Odoo system to a .XAF file according to the model provided by
the `Dutch tax  authorities <http://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/aangifte_betalen_en_toezicht/toezicht/handhaving_en_controle/belastingcontrole_met_de_auditfile>`_

--\n
This modules is based on the module `nbs_xml_auditfile_financieel <http://www.neobis.nl/>`_
developed by `Neobis ICT Dienstverlening B.V. <http://www.neobis.nl/>`_ and uses
the module `xml_template <https://www.odoo.com/apps/7.0/xml_template/>`_ created by
Swing Entwicklung betrieblicher Informationssysteme GmbH.
""",
    'author': 'ONESTEiN BV',
    'website': 'http://www.onestein.nl',
    'images': [],
    'depends': ['account_accountant', 'document', 'xml_template', ],
    'init_xml': [],
    'data': [
        'security/ir.model.access.csv',
        'auditfile_export.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
