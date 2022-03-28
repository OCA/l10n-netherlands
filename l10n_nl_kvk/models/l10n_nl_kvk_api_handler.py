# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import requests
from os.path import dirname, join, realpath

from odoo import api, models, _

_logger = logging.getLogger(__name__)


class KvkApiHandler(models.AbstractModel):
    _name = 'l10n.nl.kvk.api.handler'
    _description = 'Handler for KvK API services'

    @api.model
    def _get_config(self, val):
        """ Get configuration parameters """
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
        """ Execute search query via GET request """
        headers = self._kvk_http_header()
        request_timeout = self._get_config('timeout')

        cert_dir = realpath(join(dirname(__file__), "../data"))
        cert_file = join(cert_dir, "api_kvk_nl_bundle.crt")
        try:
            request = requests.get(
                url_query,
                headers=headers,
                verify=cert_file,
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
        except requests.exceptions.ConnectionError as err:
            _logger.warning("Connection Error: " + str(err))
            err_msg = _(
                "Network is unreachable or certificate is not valid.\n"
                "Please check your connection or try again later.\n"
                "If the problem persists, check that the “Staat der Nederlanden "
                "Private Root CA – G1” certificate chain is valid.")
            raise self.env['res.config.settings'].get_config_warning(err_msg)
        except Exception:
            _logger.warning("Unhandled exception.")
            err_msg = _("Unhandled exception.")
            raise self.env['res.config.settings'].get_config_warning(err_msg)
        return request.content

    @api.model
    def _kvk_http_header(self):
        """ Format header to contain API key/value """
        # In case of test we use the standard test value
        headers = {'apikey': 'l7xx1f2691f2520d487b902f4e0b57a0b197', }

        # In case of production, take key/value from the configuration
        if self._get_config('service') == 'kvk':
            kvk_api_key = self._get_config('kvk_api_key')
            kvk_api_value = self._get_config('kvk_api_value')
            headers = {kvk_api_key: kvk_api_value, }
        return headers

    @api.model
    def _get_url_zoeken(self):
        """ Returns Zoeken API endpoint """
        if self._get_config('service') == 'kvk':
            url_query = 'https://api.kvk.nl/api/v1/zoeken'
        else:
            url_query = 'https://api.kvk.nl/test/api/v1/zoeken'
        return url_query

    @api.model
    def _get_url_query_kvk_api(self, kvk):
        """ Format URL query to search by KvK number """
        url_query = self._get_url_zoeken()
        url_query += '?kvkNummer={0}'
        return url_query.format(kvk)

    @api.model
    def _get_url_query_name_api(self, name):
        """ Format URL query to search by company name """
        url_query = self._get_url_zoeken()
        url_query += '?handelsnaam={0}'
        return url_query.format(name)

    @api.model
    def _kvk_format_street(self, street, number, extra):
        if street and number:
            street = '%s %s%s' % (street, number, extra or '')
        return street or False
