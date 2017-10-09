# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models, fields


DEFAULT_PREFIX = {
    'shortcut': {
        'male': 'De heer',
        'female': 'Mevrouw',
        'other': '',
        'unknown': 'De heer of mevrouw',
    },
    'salutation': {
        'male': 'Geachte heer',
        'female': 'Geachte mevrouw',
        'other': 'Geachte',
        'unknown': 'Geachte heer of mevrouw',
    }
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
        # Use API from partner_firstname
        # (actually method as it has been overridden in partner_name_dutch)
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
                val = partner.title[field] or \
                    DEFAULT_PREFIX[field][partner.gender or 'unknown']
            return val and (val + ' ') or ''

        for rec in self:
            rec.salutation = False
            rec.salutation_address = False
            if rec.is_company:
                # For the moment also no manual salutations for company:
                continue
            if rec.use_manual_salutations:
                rec.salutation = rec.salutation_manual or False
                rec.salutation_address = \
                    rec.salutation_address_manual or False
            # Use API from partner_firstname
            name = rec.get_salutation_name()
            # Apply prefix/or and suffix
            if not rec.salutation:
                rec.salutation = get_prefix('salutation', rec) + name
                if rec.title.postnominal:
                    rec.salutation += ' ' + rec.title.postnominal
            if not rec.salutation_address:
                rec.salutation_address = get_prefix('shortcut', rec) + name
                if rec.title.postnominal:
                    rec.salutation_address += ' ' + rec.title.postnominal

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
