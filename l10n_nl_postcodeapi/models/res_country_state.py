# Copyright 2013-2015 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    @api.multi
    def write(self, vals):
        """
        Clear the postcode provider cache when the state
        table is altered.
        """
        self.env['res.partner'].get_province.clear_cache(
            self.env['res.partner'])
        return super(ResCountryState, self).write(vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        """
        Clear the postcode provider cache when the state
        table is altered.
        """
        self.env['res.partner'].get_province.clear_cache(
            self.env['res.partner'])
        return super(ResCountryState, self).create(vals)

    @api.multi
    def unlink(self):
        """
        Clear the postcode provider cache when the state
        table is altered.
        """
        self.env['res.partner'].get_province.clear_cache(
            self.env['res.partner'])
        return super(ResCountryState, self).unlink()
