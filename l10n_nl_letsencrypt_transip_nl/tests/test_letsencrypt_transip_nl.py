# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase
from mock import mock, patch


class TestLetsencryptTransip(TransactionCase):

    post_install = True
    at_install = False

    def setUp(self):
        super(TestLetsencryptTransip, self).setUp()
        self.key = open(self.env['letsencrypt']._generate_key(
            'test.key')).read()
        self.settings = self.env['base.config.settings'].create({
            'dns_provider': 'transip',
            'altnames': '*.example.com',
            'letsencrypt_transip_login': 'simulacra',
            'letsencrypt_transip_key': self.key,
            'reload_command': 'echo',
        })
        self.settings.set_default()
        self.settings.set_dns_provider()

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

    @patch(
        'odoo.addons.l10n_nl_letsencrypt_transip_nl.models.'
        'letsencrypt.resolver')
    @patch('odoo.addons.letsencrypt.models.letsencrypt.client')
    @patch(
        'odoo.addons.l10n_nl_letsencrypt_transip_nl.'
        'models.letsencrypt.DnsEntry')
    @patch(
        'odoo.addons.l10n_nl_letsencrypt_transip_nl.models.'
        'letsencrypt.DomainService')
    def test_invocation(self, domain_service, dns_entry, client, resolver):
        letsencrypt = self.env['letsencrypt']
        mockV2 = mock.Mock
        order_resource = mock.Mock
        order_resource.fullchain_pem = 'test'
        mockV2.poll_and_finalize = order_resource
        authorization = mock.Mock
        body = mock.Mock()
        challenge_dns = mock.Mock
        challenge_dns.chall = mock.Mock
        challenge_dns.chall.typ = 'dns-01'
        challenge_dns.chall.token = 'a_token'
        challenges = [challenge_dns]
        body.challenges = challenges
        body.identifier.value = '*.example.com'
        authorization.body = body
        mockV2.new_order = mock.Mock(
            side_effect=lambda x: mock.Mock(authorizations=[authorization]))
        client.client.ClientV2 = mockV2(create=True)
        dns_entry.return_value = mock.Mock(content='content_hash')
        query = mock.MagicMock()
        query.to_text.return_value = '"content_hash"'
        resolver.query = mock.Mock(return_value=[query])
        letsencrypt._cron()
