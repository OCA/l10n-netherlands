# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    import transip.service.domain
    import transip.service.objects
except ImportError as err:
    _logger.debug(err)


class Letsencrypt(models.AbstractModel):
    _inherit = "letsencrypt"

    @api.model
    def _respond_challenge_dns_transip(self, domain, token):
        """Create a TXT DNS record on TransIP.

        :param domain: The domain that the challenge is for.
        :param token: The token to complete the challenge.
        """
        client = self._get_transip_client()

        # We remove old records first, for two reasons:
        # - Although they don't conflict, we don't want to clutter things up.
        # - TransIP demands that all TXT records with the same name have the
        #   same TTL. The easiest way to ensure that is to only have one.
        to_remove = [
            entry
            for entry in client.get_info(domain).dnsEntries
            if entry.type == "TXT" and entry.name == "_acme-challenge"
        ]
        if to_remove:
            client.remove_dns_entries(domain, to_remove)

        dns_entry = transip.service.objects.DnsEntry(
            name="_acme-challenge",
            expire=60,
            record_type="TXT",
            content=token,
        )
        client.add_dns_entries(domain, [dns_entry])

    @api.model
    def _get_transip_client(self):
        """Get a DomainService client for TransIP using stored credentials."""
        ir_config_parameter = self.env["ir.config_parameter"]
        # The library demands str objects, unicode won't do
        login = str(ir_config_parameter.get_param("letsencrypt_transip_login"))
        key = str(ir_config_parameter.get_param("letsencrypt_transip_key"))
        return transip.service.domain.DomainService(
            login=login, private_key=key
        )
