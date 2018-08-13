# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_state_for_zip(self, country_id, state_id, zip):
        """Get state for zip.

        If not Netherlands, just return present state, unless state is
        in the Netherlands. In that case state will be False.
        """
        StateModel = self.env['res.country.state.nl.zip']

        if country_id and country_id != self.env.ref('base.nl').id:
            if not state_id:
                return False
            if StateModel.search([('state_id', '=', state_id)], limit=1):
                return False
            return state_id
        # Assume netherlands
        # Check whether we can find state for zip, if we find one, any
        # state present in record will be overwritten
        zip_digits = 0
        if zip:
            zip_digits = int(''.join([n for n in zip if n.isdigit()]))
        if not zip_digits:
            return state_id
        return StateModel.search([
            ('min_zip', '<=', zip_digits),
            ('max_zip', '>=', zip_digits)], limit=1).state_id.id

    @api.model
    def _set_state_from_zip(self, vals):
        """If country is not set, we assume it to be the Netherlands."""
        if vals.get('zip') or 'country_id' in vals:
            vals['state_id'] = self._get_state_for_zip(
                vals.get('country_id'), vals.get('state_id'), vals.get('zip'))

    @api.model
    def create(self, vals):
        self._set_state_from_zip(vals)
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        self._set_state_from_zip(vals)
        return super(ResPartner, self).write(vals)

    @api.onchange('zip')
    def onchange_zip_country_id(self):
        state_id = self._get_state_for_zip(
            self.country_id.id, self.state_id.id, self.zip)
        self.update({
            'state_id': state_id,
        })
