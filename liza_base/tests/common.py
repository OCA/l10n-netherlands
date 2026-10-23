# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

# Recording a cassette: delete the old one, set LIZA_TEST_LOGIN and
# LIZA_TEST_PASSWORD, run the test, replace the credentials in the cassette with
# lizatestlogin / lizatestpassword, then add @freeze_time("<today>"): the login
# hash depends on the date.

import os
from urllib import parse

import requests
from requests import PreparedRequest, Session
from vcr_unittest import VCRMixin

from odoo.addons.base.tests.common import BaseCommon

_super_send = requests.Session.send

TEST_LOGIN = "lizatestlogin"
TEST_PASSWORD = "lizatestpassword"


class LizaTestCommon(VCRMixin, BaseCommon):
    # Subclasses set this to the hostname(s) their API lives on.
    LIZA_ALLOWED_HOSTNAMES = ()

    @classmethod
    def _request_handler(cls, s: Session, r: PreparedRequest, /, **kw):
        """Odoo blocks non-localhost requests; allow the Liza API hosts."""
        url = parse.urlparse(r.url)
        if url.hostname in cls.LIZA_ALLOWED_HOSTNAMES:
            return _super_send(s, r, **kw)
        return super()._request_handler(s=s, r=r, **kw)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

    def _set_credentials(self):
        self.company.liza_login = os.environ.get("LIZA_TEST_LOGIN", TEST_LOGIN)
        self.company.liza_password = os.environ.get("LIZA_TEST_PASSWORD", TEST_PASSWORD)

    def _get_vcr_kwargs(self, **kwargs):
        return {
            "record_mode": "once",
            "match_on": ["method", "path", "query"],
            "filter_headers": ["Authorization"],
            "decode_compressed_response": True,
        }
