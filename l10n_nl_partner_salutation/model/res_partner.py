# -*- coding: utf-8 -*-

GENDERS = [('male', 'Male'), ('female', 'Female'), ('unknown', 'Unknown')]


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    def on_change_use_manual_salutations(
            self, cr, uid, ids, use_salutation_manual,
            salutation, salutation_address, context=None):
        if not use_salutation_manual:
            return {}
        return {
            'value': {
                'salutation_manual': salutation,
                'salutation_address_manual': salutation_address,
            }
        }

    def get_salutation_name_format(self):
        """Return the desired name format for use in the salutation."""
        return (
            "${p.firstname or p.initials or ''}"
            "${' ' if (p.firstname or p.initials) else ''}"
            "${p.infix or ''}"
            "${' ' if p.infix else ''}"
            "${p.lastname or ''}"
        )

    def on_change_use_manual_salutations(
            self, cr, uid, ids, use_salutation_manual,
            salutation, salutation_address, context=None):
        if not use_salutation_manual:
            return {}
        return {
            'value': {
                'salutation_manual': salutation,
                'salutation_address_manual': salutation_address,
            }
        }

    @api.depends(
        'gender',
        'title',
        'use_manual_salutations',
        'salutation',
        'salutation_address'
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
        name_format = self.get_salutation_name_format(),

        for rec in self:
            """
            Compose salutation for letters and addresses by applying
            generized prefixes and optional suffix to the display name.
            """
            if rec.use_manual_salutations:
                rec.salutation = rec.salutation_manual
                rec.salutation_address = rec.salutation_address_manual
                continue

            # Use API from partner_firstname
            name = self.with_context(
                name_format=name_format)._prepare_name_custom(rec) or ''
            # Apply prefix/or and suffix
            rec.salutation = get_prefix('salutation', rec) + name
            rec.salutation_address = get_prefix('shortcut', rec) + name
            if rec.title.postnominal:
                rec.salutation += ' ' + rec.title.postnominal
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
