# -*- coding: utf-8 -*-
# © 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        vals = self._state_from_vals(vals)
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        vals = self._state_from_vals(vals)
        return super(ResPartner, self).write(vals)

    @api.model
    def _state_from_vals(self, vals):
        if 'zip' not in vals or 'state_id' in vals:
            return vals
        if 'country_id' in vals and vals['country_id'] != self.env.ref(
                'base.nl'
        ).id:
            return vals
        zip_digits = int(
            filter(unicode.isdigit, unicode(vals['zip'] or '')) or 0
        )
        return dict(
            vals,
            state_id=self.env['res.country.state.nl.zip'].search([
                ('min_zip', '<=', zip_digits),
                ('max_zip', '>=', zip_digits),
            ]).state_id.id,
        )

    @api.onchange('zip')
    def onchange_zip_country_id(self):
        state_id = self._state_from_vals({
            'zip': self.zip,
            'country_id': self.country_id.id,
        }).get('state_id')
        self.state_id = self.env['res.country.state'].browse(state_id or [])
