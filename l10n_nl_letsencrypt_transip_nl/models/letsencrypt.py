# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, models
from odoo.exceptions import UserError

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

        # We need to figure out which TransIP domain name is responsible for
        # the domain we need to change, in case of subdomains.
        # We need to be able to handle both *.foo.bar.nl and *.foo.bar.co.uk so
        # we can't make a lot of assumptions.
        domain = domain.rstrip(".")
        for available_domain in client.get_domain_names():
            if available_domain == domain:
                target_domain = domain
                subdomain = "_acme-challenge"
                break
            elif domain.endswith("." + available_domain):
                # Cast because it's a weird suds value
                target_domain = str(available_domain)
                subdomain = (
                    "_acme-challenge." + domain[: -(len(available_domain) + 1)]
                )
                break
        else:
            raise UserError(
                _("Can't find an appropriate TransIP domain for %s!") % domain
            )

        # We remove old records first, for two reasons:
        # - Although they don't conflict, we don't want to clutter things up.
        # - TransIP demands that all TXT records with the same name have the
        #   same TTL. The easiest way to ensure that is to only have one.
        to_remove = [
            entry
            for entry in client.get_info(target_domain).dnsEntries
            if entry.type == "TXT" and entry.name == subdomain
        ]
        if to_remove:
            client.remove_dns_entries(target_domain, to_remove)

        dns_entry = transip.service.objects.DnsEntry(
            name=subdomain,
            expire=60,
            record_type="TXT",
            content=token,
        )
        client.add_dns_entries(target_domain, [dns_entry])

    @api.model
    def _get_transip_client(self):
        """Get a DomainService client for TransIP using stored credentials."""
        ir_config_parameter = self.env["ir.config_parameter"]
        login = ir_config_parameter.get_param("letsencrypt_transip_login")
        key = ir_config_parameter.get_param("letsencrypt_transip_key")
        return transip.service.domain.DomainService(
            login=login, private_key=key
        )
