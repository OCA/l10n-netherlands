# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import os
import shutil
import tempfile

from mock import mock, patch

from odoo.tests.common import TransactionCase


class TestLetsencryptTransip(TransactionCase):

    post_install = True
    at_install = False

    def setUp(self):
        super(TestLetsencryptTransip, self).setUp()
        self.key = "somekey"
        self.settings = self.env['res.config.settings'].create({
            'letsencrypt_dns_provider': 'transip',
            'letsencrypt_altnames': '*.example.com',
            'letsencrypt_transip_login': 'simulacra',
            'letsencrypt_transip_key': self.key,
            'letsencrypt_reload_command': 'echo',
        })
        self.settings.set_values()
        self.env["ir.config_parameter"].set_param(
            "web.base.url", "http://example.com"
        )
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        super(TestLetsencryptTransip, self).tearDown()
        if os.path.isdir(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def test_settings(self):
        vals = self.settings.default_get([])
        self.assertEquals(
            vals['letsencrypt_transip_login'],
            'simulacra',
        )
        self.assertEquals(
            vals['letsencrypt_transip_key'],
            self.key,
        )

    @patch("transip.service.domain.DomainService")
    def test_invocation(self, domain_service):
        client = domain_service.return_value

        entry = mock.Mock()
        entry.type = "TXT"
        entry.name = "_acme-challenge"
        client.get_info.return_value.dnsEntries = [entry]
        client.get_domain_names.return_value = ["example.com", "example.org"]

        def check_add_call(domain, entries):
            self.assertEquals(domain, "example.com")
            self.assertEquals(len(entries), 1)
            self.assertEquals(entries[0].name, "_acme-challenge")
            self.assertEquals(entries[0].type, "TXT")
            self.assertEquals(entries[0].content, "a_token")

        client.add_dns_entries.side_effect = check_add_call

        self.env["letsencrypt"]._respond_challenge_dns_transip(
            "example.com", "a_token"
        )

        domain_service.assert_called_with(
            login="simulacra", private_key="somekey"
        )
        client.get_info.assert_called()
        client.remove_dns_entries.assert_called_with("example.com", [entry])
        client.add_dns_entries.assert_called()

    @patch("transip.service.domain.DomainService")
    def test_invocation_with_subdomain(self, domain_service):
        client = domain_service.return_value

        client.get_info.return_value.dnsEntries = []
        client.get_domain_names.return_value = ["example.com", "example.org"]

        def check_add_call(domain, entries):
            self.assertEquals(domain, "example.com")
            self.assertEquals(len(entries), 1)
            self.assertEquals(entries[0].name, "_acme-challenge.foo.bar")
            self.assertEquals(entries[0].type, "TXT")
            self.assertEquals(entries[0].content, "a_token")

        client.add_dns_entries.side_effect = check_add_call

        self.env["letsencrypt"]._respond_challenge_dns_transip(
            "foo.bar.example.com", "a_token"
        )

        domain_service.assert_called_with(
            login="simulacra", private_key="somekey"
        )
        client.get_info.assert_called()
        client.add_dns_entries.assert_called()
