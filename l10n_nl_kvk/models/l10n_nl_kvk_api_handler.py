# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import requests

from odoo import api, models, _

_logger = logging.getLogger(__name__)


class KvkApiHandler(models.AbstractModel):
    _name = 'l10n.nl.kvk.api.handler'
    _description = 'Handler for KvK API services'

    @api.model
    def _get_config(self, val):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        config_dict = {
            'service': get_param('l10n_nl_kvk_service', 'test'),
            'timeout': int(get_param('l10n_nl_kvk_timeout', 3)),
            'kvk_api_key': get_param('l10n_nl_kvk_api_key'),
            'kvk_api_value': get_param('l10n_nl_kvk_api_value'),
        }
        return config_dict[val]

    @api.model
    def _retrieve_data_by_api(self, url_query):

        headers = self._kvk_http_header()
        request_timeout = self._get_config('timeout')

        try:
            request = requests.get(
                url_query,
                headers=headers,
                timeout=request_timeout)
            request.raise_for_status()
        except requests.HTTPError as error:
            if error.response.status_code == 400:
                # HTTP Error 400: Bad Request
                _logger.warning("HTTP Error 400: Bad Request")
                err_msg = _(
                    "KvK keys are not correct.\n"
                    "Please check the KvK API configuration.")
            elif error.response.status_code == 401:
                # HTTP Error 401: Unauthorized
                _logger.warning("HTTP Error 401: Unauthorized")
                err_msg = _(
                    "The server returned a 'Error 401: Unauthorized'.\n"
                    "Probably the KvK keys are not correct.\n"
                    "Please check the KvK API configuration.")
            elif error.response.status_code == 500:
                # HTTP Error 500: Internal Server Error
                _logger.warning("HTTP Error 500: Internal Server Error")
                err_msg = _(
                    "The API service server had an 'Internal Server Error'.\n"
                    "Hopefully it is a temporary error.")
            else:
                _logger.warning("Unhandled HTTPError exception.")
                err_msg = _(
                    "Unhandled HTTPError exception.")
            raise self.env['res.config.settings'].get_config_warning(err_msg)
        except requests.exceptions.ConnectionError:
            _logger.warning("[Errno 101]: Network is unreachable")
            err_msg = _(
                "Network is unreachable.\n"
                "Please check your connection.")
            raise self.env['res.config.settings'].get_config_warning(err_msg)
        except Exception:
            _logger.warning("Unhandled exception.")
            err_msg = _("Unhandled exception.")
            raise self.env['res.config.settings'].get_config_warning(err_msg)
        return request.content

    @api.model
    def _kvk_http_header(self):
        headers = {'test': 'test', }
        if self._get_config('service') == 'kvk':
            kvk_api_key = self._get_config('kvk_api_key')
            kvk_api_value = self._get_config('kvk_api_value')
            headers = {kvk_api_key: kvk_api_value, }
        return headers

    @api.model
    def _get_url_query_kvk_api(self, kvk):
        url_query = 'https://api.kvk.nl/api/v2/'

        if self._get_config('service') == 'kvk':
            url_query += 'search/companies?kvkNumber={0}'
        else:
            url_query += 'testsearch/companies?kvkNumber={0}'

        url_query = url_query.format(kvk)
        return url_query

    @api.model
    def _get_url_query_name_api(self, name):
        url_query = 'https://api.kvk.nl/api/v2/testsearch/companies?q={0}'

        if self._get_config('service') == 'kvk':
            url_query = 'https://api.kvk.nl/api/v2/search/companies?q={0}'
            url_query = url_query.format(name)

        url_query = url_query.format(name)
        return url_query

    @api.model
    def _kvk_format_street(self, street, number, extra):
        if street and number:
            street = '%s %s%s' % (street, number, extra or '')
        return street or False
