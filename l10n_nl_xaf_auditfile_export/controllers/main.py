# -*- coding: utf-8 -*-
# Copyright 2017-2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import content_disposition

from ..models.xaf_auditfile_export import get_auditfile_path


class Main(http.Controller):

    @http.route('/file_cabinet/auditfile', type='http', auth='user')
    def auditfile(self, filename):
        """Serve auditfile"""
        auditfile_path = get_auditfile_path(filename)
        with open(auditfile_path) as infile:
            filecontent = infile.read()
        return request.make_response(
            filecontent,
            [('Content-Type', 'text/plain'),
             ('Content-Disposition', content_disposition(filename))])
