#!/usr/bin/python

import argparse
import xmlrpclib
import re
parser = argparse.ArgumentParser()
parser.add_argument('openerp_host')
parser.add_argument('openerp_db')
parser.add_argument('openerp_user')
parser.add_argument('openerp_passwd')
parser.add_argument('additional_search', nargs='?')
args = parser.parse_args()

openerp_socket = xmlrpclib.ServerProxy(
    'http://%s/xmlrpc/common' % args.openerp_host)
openerp_uid = openerp_socket.login(
    args.openerp_db, args.openerp_user, args.openerp_passwd)
openerp_socket = xmlrpclib.ServerProxy(
    'http://%s/xmlrpc/object' % args.openerp_host, allow_none=True)


def openerp_execute(model, method, *pargs, **kwargs):
    return openerp_socket.execute(
        args.openerp_db, openerp_uid,
        args.openerp_passwd, model, method, *pargs, **kwargs)

infixes = ['van', 'der', 'ter', 'de', 'v/d']
initial = re.compile(r'^([A-Z]{1,3}\.{0,1}){1,4}$')

limit = 100000
offset = 0


def add_token(values, key, token, delimiter=' '):
    values[key] = (values[key] + ' ' if values[key] else '') + token

while True:
    ids = openerp_execute(
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

    for partner in openerp_execute(
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
        openerp_execute('res.partner', 'write', partner['id'], partner)

    offset += limit
