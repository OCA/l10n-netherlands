# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from werkzeug import url_encode, url_quote_plus

from odoo import api, models

_logger = logging.getLogger(__name__)


class KvkApiHandler(models.AbstractModel):
    _inherit = 'l10n.nl.kvk.api.handler'

    @api.model
    def _kvk_http_header(self):
        if self._get_config('service') != 'openkvk':
            return super()._kvk_http_header()

        get_param = self.env['ir.config_parameter'].sudo().get_param
        return {'ovio-api-key': get_param('l10n_nl_openkvk_api_value'), }

    @api.model
    def _get_url_query_kvk_api(self, kvk):
        if self._get_config('service') != 'openkvk':
            return super()._get_url_query_kvk_api(kvk)

        params = url_encode({url_quote_plus('fields[]'): 'dossiernummer'})
        url = 'https://api.overheid.io/suggest/openkvk/{0}?'
        url = url.format(kvk)
        return url + params

    @api.model
    def _get_url_query_name_api(self, name):
        if self._get_config('service') != 'openkvk':
            return super()._get_url_query_name_api(name)

        params = url_encode({url_quote_plus('fields[]'): 'handelsnaam'})
        url = 'https://api.overheid.io/suggest/openkvk/{0}?'
        url = url.format(name)
        return url + params
