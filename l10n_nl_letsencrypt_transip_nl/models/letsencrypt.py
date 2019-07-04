# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models
from time import sleep
import base64
import logging

_logger = logging.getLogger(__name__)

try:
    from transip.service.objects import DnsEntry
    from transip.service.domain import DomainService
    import josepy as jose
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.backends import default_backend
    from dns import resolver
except ImportError as err:
    _logger.debug(err)


class Letsencrypt(models.AbstractModel):
    _inherit = 'letsencrypt'

    def _respond_challenge_dns_transip(self, challenge, account_key, domain):
        """_respond_challenge_dns_transip Creates the TXT record on TransIP.

        :param challenge: An acme.challenges.Challenge object that contains
                          relevant data for this challenge.
        :param domain: A str. The domain that the challenge is for.
        """
        ir_config_parameter = self.env['ir.config_parameter']
        login = ir_config_parameter.get_param('letsencrypt_transip_login')
        key = ir_config_parameter.get_param('letsencrypt_transip_key')
        token = base64.urlsafe_b64encode(challenge.token)
        dns_entry = DnsEntry(
            '_acme-challenge',
            86400,
            'TXT',
            token.rstrip('=') + '.' + jose.b64encode(
                account_key.thumbprint(hash_function=hashes.SHA256)).decode(),
        )
        key = serialization.load_pem_private_key(
            str(key),
            password=None,
            backend=default_backend())
        key = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption())
        domain = domain.replace('*.', '')
        DomainService(login, key).add_dns_entries(domain, [dns_entry])
        self._validate_record(login, key, domain, dns_entry)

    def _validate_record(self, login, key, domain, dns_entry):
        """ This function is a safety-net in order to avoid the following:
        1)  Since there can be multiple txt records with the same name, remove
            them all and keep only the one we have created
        2)  If, for some reason, the first dns validation fails and we go ahead
            and do another one, letsencrypt will "look" at the old txt record,
            here we wait a little bit.
        """
        dns_entries = DomainService(login, key).get_info(domain).dnsEntries
        to_remove = filter(
            lambda x: x.type == DnsEntry.TYPE_TXT
            and x.content != dns_entry.content
            and x.name == dns_entry.name,
            dns_entries)
        if to_remove:
            DomainService(login, key).remove_dns_entries(domain, to_remove)
        values = []
        while dns_entry.content not in values:
            if values:
                _logger.info('Waiting for DNS update.')
                sleep(60)
            for data in resolver.query(
                    '_acme-challenge.' + domain, 'TXT'):
                values.append(data.to_text()[1:-1])  # remove quotes
