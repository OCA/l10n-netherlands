# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models, fields

GENDERS = [('male', 'Male'), ('female', 'Female'), ('unknown', 'Unknown')]


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
        """Return the desired name format for use in the salutation."""
        return (
            "${firstname or initials or ''}"
            "${' ' if (firstname or initials) else ''}"
            "${infix or ''}"
            "${' ' if infix else ''}"
            "${lastname or ''}"
        )

    @api.depends(
        'gender',
        'title',
        'use_manual_salutations',
        'salutation_manual',
        'salutation_address_manual'
    )
    def _compute_salutation(self):
        """Return the salutation fields."""

        def get_prefix(field, partner):
            """
            Get genderized values for the given field, with a fallback
            on the field if the partner has no gender or the genderized
            field itself has no value.
            """
            val = ''
            if partner.gender in ('male', 'female'):
                val = partner.title[field + '_' + partner.gender]
            if not val:
                val = partner.title[field] or default_prefix[
                    field][partner.gender or 'unknown']
            return val + ' '

        default_prefix = {
            'shortcut': {
                'male': 'De heer',
                'female': 'Mevrouw',
                'unknown': 'De heer of mevrouw',
            },
            'salutation': {
                'male': 'Geachte heer',
                'female': 'Geachte mevrouw',
                'unknown': 'Geachte heer of mevrouw',
            }
        }
        name_format = self.get_salutation_name_format()
        for rec in self:
            rec.salutation = False
            rec.salutation_address = False
            if rec.use_manual_salutations:
                rec.salutation = rec.salutation_manual or False
                rec.salutation_address = rec.salutation_address_manual or False
            # Use API from partner_firstname
            name = self.with_context(name_format=name_format)\
                ._get_computed_name(
                    rec.lastname, rec.firstname, initials=rec.initials,
                    infix=rec.infix)
            # Apply prefix/or and suffix
            if not rec.salutation:
                rec.salutation = get_prefix('salutation', rec) + name
                if rec.title.postnominal:
                    rec.salutation += ' ' + rec.title.postnominal
            if not rec.salutation_address:
                rec.salutation_address = get_prefix('shortcut', rec) + name
                if rec.title.postnominal:
                    rec.salutation_address += ' ' + rec.title.postnominal

    gender = fields.Selection(GENDERS, required=True, default='unknown')
    salutation = fields.Char(
        compute='_compute_salutation',
        string='Salutation (letter)'
    )
    salutation_address = fields.Char(
        compute='_compute_salutation',
        string='Salutation (address)'
    )
    use_manual_salutations = fields.Boolean('Enter salutations manually')
    salutation_manual = fields.Char('Manual salutation (letter)')
    salutation_address_manual = fields.Char('Manual salutation (address)')
