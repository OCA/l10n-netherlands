#!/usr/bin/python
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import argparse
import xmlrpclib
import re
parser = argparse.ArgumentParser()
parser.add_argument('odoo_host')
parser.add_argument('odoo_db')
parser.add_argument('odoo_user')
parser.add_argument('odoo_passwd')
parser.add_argument('additional_search', nargs='?')
args = parser.parse_args()

odoo_socket = xmlrpclib.ServerProxy(
    'http://%s/xmlrpc/common' % args.odoo_host)
odoo_uid = odoo_socket.login(
    args.odoo_db, args.odoo_user, args.odoo_passwd)
odoo_socket = xmlrpclib.ServerProxy(
    'http://%s/xmlrpc/object' % args.odoo_host, allow_none=True)


def odoo_execute(model, method, *pargs, **kwargs):
    return odoo_socket.execute(
        args.odoo_db, odoo_uid,
        args.odoo_passwd, model, method, *pargs, **kwargs)


infixes = ['van', 'der', 'ter', 'de', 'v/d']
initial = re.compile(r'^([A-Z]{1,3}\.{0,1}){1,4}$')

limit = 100000
offset = 0


def add_token(values, key, token, delimiter=' '):
    values[key] = (values[key] + ' ' if values[key] else '') + token


while True:
    ids = odoo_execute(
        'res.partner', 'search',
        [
            ('lastname', '!=', False),
            ('lastname', '!=', ''),
            ('firstname', '=', False),
            ('initials', '=', False),
            ('infix', '=', False),
            ('is_company', '=', False),
        ] +
        eval(args.additional_search or '[]'),
        offset,
        limit)
    if not ids:
        break

    for partner in odoo_execute(
            'res.partner', 'read', ids,
            ['lastname', 'firstname', 'initials', 'infix']):
        print partner['lastname']

        have_infix = False
        tokens = partner['lastname'].split()
        while len(tokens) > 1:
            token = tokens.pop(0)
            if initial.match(token):
                add_token(partner, 'initials', token)
            elif any(map(lambda infix: re.match(infix, token, re.I), infixes)):
                add_token(partner, 'infix', token.lower())
                have_infix = True
            else:
                if have_infix:
                    tokens.insert(0, token)
                    break
                add_token(partner, 'firstname', token)
        partner['lastname'] = ' '.join(tokens)

        print partner
        odoo_execute('res.partner', 'write', partner['id'], partner)

    offset += limit
