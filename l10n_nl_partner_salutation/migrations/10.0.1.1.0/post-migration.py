# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):

    cr.execute(
        "UPDATE res_partner SET gender = NULL where gender = 'unknown'"
    )
