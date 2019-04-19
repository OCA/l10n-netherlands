# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=protected-access
from openerp import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_state_for_zip(self, country_id, state_id, zipcode):
        """Get state for zipcode.

        If not Netherlands, just return present state, unless state is
        in the Netherlands. In that case state will be False.
        """
        country_nl = self.env.ref('base.nl')
        dutch_state_model = self.env['res.country.state.nl.zip']
        state_model = self.env['res.country.state']
        no_state = state_model.browse([])
        if country_id and country_id != country_nl:
            if state_id:
                dutch_state = dutch_state_model.search([
                    ('state_id', '=', state_id.id)], limit=1)
                if dutch_state:
                    return no_state
            return state_id
        # Assume netherlands
        # Check wether we can find state for zip, if we find one, any
        # state present in record will be overwritten
        zip_digits = int(
            filter(unicode.isdigit, unicode(zipcode or '')) or 0)
        if not zip_digits:
            return state_id
        zip_state = dutch_state_model.search([
            ('min_zip', '<=', zip_digits),
            ('max_zip', '>=', zip_digits)], limit=1)
        if not zip_state:
            return state_id
        return zip_state.state_id

    @api.multi
    def _set_state_from_zip(self):
        """If country is not set, we assume it to be the Netherlands."""
        for this in self:
            state_id = self._get_state_for_zip(
                this.country_id, this.state_id, this.zip)
            if state_id != this.state_id:
                super(ResPartner, this).write({'state_id': state_id.id})

    @api.model
    def create(self, vals):
        """Lookup state for zip, if state_id not passed in vals."""
        result = super(ResPartner, self).create(vals)
        if 'state_id' not in vals:
            result._set_state_from_zip()
        return result

    @api.multi
    def write(self, vals):
        """Lookup state for zip, if state_id not passed in vals."""
        result = super(ResPartner, self).write(vals)
        if 'state_id' not in vals:
            self._set_state_from_zip()
        return result

    @api.onchange('zip')
    def onchange_zip_country_id(self):
        """Change state if zip changes."""
        self.state_id = self._get_state_for_zip(
            self.country_id, self.state_id, self.zip)
