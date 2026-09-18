# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

# How to create a cassette-based test:
# 1. Write the test function.
# 1.a Ensure all non-request logic works first (fix any failures unrelated to the
#     API call, e.g. Liza status 101 or 303).
# 1.b Delete the existing cassette in tests/cassettes if one already exists.
# 2. Set env variables with real credentials:
#     LIZA_TEST_LOGIN=*****
#     LIZA_TEST_PASSWORD=*****
# 3. Run the test — a cassette is recorded in tests/cassettes/.
# 4. In the cassette, replace the real login/password with:
#     lizatestlogin / lizatestpassword
# 5. Remove the env variables.
# 6. Add @freeze_time("<today>") — the login hash is date-dependent.
# 7. Run the test to confirm it passes from the cassette.

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
        """Allow requests to Liza API hosts.
        Odoo blocks non-localhost by default."""
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
