#!/usr/bin/python
# Copyright 2017-2022 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Script to convert names using a Dutch specific guessing strategy."""
# pylint: disable=invalid-name,eval-used

import argparse
import ast
import logging
import re
import xmlrpc.client as xmlrpclib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("odoo_host")
parser.add_argument("odoo_db")
parser.add_argument("odoo_user")
parser.add_argument("odoo_passwd")
parser.add_argument("additional_search", nargs="?")
args = parser.parse_args()

extra_domain = (
    ast.literal_eval(args.additional_search) if args.additional_search else []
)

odoo_socket = xmlrpclib.ServerProxy("http://%s/xmlrpc/common" % args.odoo_host)
odoo_uid = odoo_socket.login(args.odoo_db, args.odoo_user, args.odoo_passwd)
odoo_socket = xmlrpclib.ServerProxy(
    "http://%s/xmlrpc/object" % args.odoo_host, allow_none=True
)


def odoo_execute(model, method, *pargs, **kwargs):
    """Execute a model method on Odoo through xmlrpc."""
    return odoo_socket.execute(
        args.odoo_db, odoo_uid, args.odoo_passwd, model, method, *pargs, **kwargs
    )


field_names = ["lastname", "firstname", "initials", "infix"]
infixes = ["van", "der", "ter", "de", "v/d"]
initial = re.compile(r"^([A-Z]{1,3}\.{0,1}){1,4}$")

limit = 10000
offset = 0


def add_token(values, key, token):
    """Add a name part to the correct field value of the partner names."""
    values[key] = (values[key] + " " if values[key] else "") + token


def update_partner(partner):
    """Update a single partner, reading old fields, adjusting names."""
    saved_lastname = partner["lastname"]
    have_infix = False
    tokens = partner["lastname"].split()
    while len(tokens) > 1:
        token = tokens.pop(0)
        if initial.match(token):
            add_token(partner, "initials", token)
        elif any(map(lambda infix: re.match(infix, token, re.I), infixes)):
            add_token(partner, "infix", token.lower())
            have_infix = True
        else:
            if have_infix:
                tokens.insert(0, token)
                break
            add_token(partner, "firstname", token)
    new_lastname = " ".join(tokens)
    logger.info("Lastname was %s, lastname = %s", saved_lastname, new_lastname)
    partner["lastname"] = new_lastname
    odoo_execute("res.partner", "write", partner["id"], partner)


def get_partner_ids():
    """Search next batch of partners to process."""
    return odoo_execute(
        "res.partner",
        "search",
        [
            ("lastname", "!=", False),
            ("lastname", "!=", ""),
            ("firstname", "=", False),
            ("initials", "=", False),
            ("infix", "=", False),
            ("is_company", "=", False),
        ]
        + extra_domain,
        offset,
        limit,
    )


def process_partners():
    """Read and process partners."""
    for partner in odoo_execute("res.partner", "read", ids, field_names):
        update_partner(partner)


while True:
    ids = get_partner_ids()
    if not ids:
        break
    process_partners()
    offset += limit
