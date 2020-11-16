# Copyright 2017-2020 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=no-self-use,protected-access
"""Functionality to define salutations to use in mails and letters to partners."""
from odoo import api, models, fields


DEFAULT_SHORTCUT = {
    'male': 'De heer',
    'female': 'Mevrouw',
    'other': '',
    'unknown': 'De heer of mevrouw',
}
DEFAULT_SALUTATION = {
    'male': 'Geachte heer',
    'female': 'Geachte mevrouw',
    'other': 'Geachte',
    'unknown': 'Geachte heer of mevrouw',
}


class ResPartner(models.Model):
    """Extend res.partner model."""
    _inherit = 'res.partner'

    @api.onchange('use_manual_salutations')
    def on_change_use_manual_salutations(self):
        """Handle onchange event."""
        if self.use_manual_salutations:
            # When changing to manual salutation, initially
            # use the computed fields for default.
            self.salutation_manual = self.salutation
            self.salutation_address_manual = self.salutation_address

    @api.model
    def get_salutation_name_format(self):
        """Return the name format for use in salutation."""
        return (
            "${firstname or initials or ''}"
            "${' ' if (firstname or initials) else ''}"
            "${infix or ''}"
            "${' ' if infix else ''}"
            "${lastname or ''}"
        )

    @api.multi
    def get_salutation_name(self):
        """Return the name formatted for use in salutation."""
        self.ensure_one()
        # Use _get_computed_name from partner_firstname.
        # (actually method as it has been overridden in l10n_nl_partner_name_dutch).
        return self.with_context(
            name_format=self.get_salutation_name_format()
        )._get_computed_name(
            self.lastname, self.firstname, initials=self.initials,
            infix=self.infix
        )

    @api.depends(
        'gender',
        'title',
        'use_manual_salutations',
        'salutation_manual',
    )
    def _compute_salutation(self):
        """Fill salutation field."""
        for this in self:
            this.salutation = (
                this.salutation_manual if this.use_manual_salutations
                else this._compute_salutation_field('salutation', DEFAULT_SALUTATION)
            )

    @api.depends(
        'gender',
        'title',
        'use_manual_salutations',
        'salutation_address_manual',
    )
    def _compute_salutation_address(self):
        """Fill salutation_address field."""
        for this in self:
            this.salutation_address = (
                this.salutation_address_manual if this.use_manual_salutations
                else this._compute_salutation_field('shortcut', DEFAULT_SHORTCUT)
            )

    def _compute_salutation_field(self, prefix_type, default_dict):
        """Compute salutation or salutation_address."""
        # For the moment no manual salutations for company.
        # pylint: disable=consider-using-ternary
        return (
            not self.is_company and " ".join(
                name_part for name_part in (
                    self._get_prefix(prefix_type, default_dict),
                    self.get_salutation_name(),
                    self.title.postnominal,
                )
                if name_part
            )
            or ""
        )

    def _get_prefix(self, prefix_type, default_dict):
        """Get prefix, dependend on gender."""
        self.ensure_one()
        return (
            self.gender in ('male', 'female')
            and self.title[prefix_type + '_' + self.gender]
            or self.title[prefix_type]
            or default_dict[self.gender or 'unknown']
        )

    salutation = fields.Char(
        compute='_compute_salutation',
        string='Salutation (letter)'
    )
    salutation_address = fields.Char(
        compute='_compute_salutation_address',
        string='Salutation (address)'
    )
    use_manual_salutations = fields.Boolean('Enter salutations manually')
    salutation_manual = fields.Char('Manual salutation (letter)')
    salutation_address_manual = fields.Char('Manual salutation (address)')
