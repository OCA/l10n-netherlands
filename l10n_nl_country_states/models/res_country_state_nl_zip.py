# Copyright 2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResCountryStateNlZip(models.Model):
    _name = 'res.country.state.nl.zip'
    _description = 'Map zip code areas to states'

    state_id = fields.Many2one('res.country.state', required=True)
    min_zip = fields.Integer('Low boundary of zip code area', required=True)
    max_zip = fields.Integer('High boundary of zip code area', required=True)
