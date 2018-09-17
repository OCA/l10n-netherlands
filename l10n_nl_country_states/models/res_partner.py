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
        country_nl = self.env.ref('base.nl')
        StateModel = self.env['res.country.state.nl.zip']
        state_model = self.env['res.country.state']
        no_state = state_model.browse([])
        if country_id and country_id != country_nl:
            if state_id:
                dutch_state = StateModel.search([
                    ('state_id', '=', state_id.id)], limit=1)
                if dutch_state:
                    return no_state
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
            ('max_zip', '>=', zip_digits)], limit=1).state_id

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
        result = super(ResPartner, self).create(vals)
        result._set_state_from_zip()
        return result

    @api.multi
    def write(self, vals):
        result = super(ResPartner, self).write(vals)
        self._set_state_from_zip()
        return result

    @api.onchange('zip')
    def onchange_zip_country_id(self):
        self.state_id = self._get_state_for_zip(
            self.country_id, self.state_id, self.zip)
