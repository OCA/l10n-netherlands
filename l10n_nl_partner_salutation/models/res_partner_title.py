# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class ResPartnerTitle(models.Model):
    """Extend res.partner.title model."""
    _inherit = 'res.partner.title'

    salutation = fields.Char(size=64, translate=True)
    salutation_male = fields.Char(string='Salutation male')
    salutation_female = fields.Char(string='Salutation female')
    shortcut_male = fields.Char(string='Shortcut male')
    shortcut_female = fields.Char(string='Shortcut female')
    postnominal = fields.Char(string='Postnominal')
