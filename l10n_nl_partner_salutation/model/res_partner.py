# -*- coding: utf-8 -*-
"""Extend res.partner model."""
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014-2015 Therp BV <http://therp.nl>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import api, models, fields

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
    def _get_salutation(self):
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
        compute='_get_salutation',
        string='Salutation (letter)'
    )
    salutation_address = fields.Char(
        compute='_get_salutation',
        string='Salutation (address)'
    )
    use_manual_salutations = fields.Boolean('Enter salutations manually')
    salutation_manual = fields.Char('Manual salutation (letter)')
    salutation_address_manual = fields.Char('Manual salutation (address)')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
