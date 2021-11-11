# Copyright 2018-2021 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=protected-access
from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_state_for_zip(self, country_id, state_id, postalcode):
        """Get state for postalcode.

        If not Netherlands, just return present state, unless state is
        in the Netherlands. In that case state will be False.
        """
        country_nl = self.env.ref("base.nl")
        postalcode_model = self.env["res.country.state.nl.zip"]
        state_model = self.env["res.country.state"]
        no_state = state_model.browse([])
        if country_id and country_id != country_nl:
            if state_id:
                # If we are not in the Netherlands, but partner refers to a
                # dutch state, clear the state.
                dutch_state = postalcode_model.search(
                    [("state_id", "=", state_id.id)], limit=1
                )
                if dutch_state:
                    return no_state
            return state_id
        # Assume netherlands
        # Check whether we can find state for postalcode, if we find one, any
        # state present in record will be overwritten
        postalcode_digits = 0
        if postalcode:
            postalcode_digits = int("".join([n for n in postalcode if n.isdigit()]))
        if not postalcode_digits:
            return state_id
        return postalcode_model.search(
            [
                ("min_zip", "<=", postalcode_digits),
                ("max_zip", ">=", postalcode_digits),
            ],
            limit=1,
        ).state_id

    @api.multi
    def _set_state_from_zip(self):
        """If country is not set, we assume it to be the Netherlands."""
        for this in self:
            state_id = self._get_state_for_zip(this.country_id, this.state_id, this.zip)
            if state_id != this.state_id:
                super(ResPartner, this).write({"state_id": state_id.id})

    @api.model
    def create(self, vals):
        """Make sure that after create state has been set from zip where possible."""
        result = super().create(vals)
        result._set_state_from_zip()
        return result

    @api.multi
    def write(self, vals):
        """Make sure that after write state has been set from zip where possible."""
        result = super().write(vals)
        self._set_state_from_zip()
        return result

    @api.onchange("zip")
    def onchange_zip_country_id(self):
        """Set state when zip changes."""
        self.state_id = self._get_state_for_zip(
            self.country_id, self.state_id, self.zip
        )
