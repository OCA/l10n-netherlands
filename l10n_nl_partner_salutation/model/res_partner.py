from openerp.osv import orm, fields

GENDERS = [('male', 'Male'), ('female', 'Female'), ('unknown', 'Unknown')]


class Partner(orm.Model):
    _inherit = 'res.partner'

    def get_salutation_name_format(self, cr, uid, context=None):
        """
        Return the desired name format for use in the salutation
        """
        return (
            "${p.firstname or p.initials or ''}"
            "${' ' if (p.firstname or p.initials) else ''}"
            "${p.infix or ''}"
            "${' ' if p.infix else ''}"
            "${p.lastname or ''}"
            )

    def _get_salutation(self, cr, uid, ids, field_name, args, context=None):
        """
        Return the salutation fields
        """
        result = {}
        context = dict(
            context, name_format=self.get_salutation_name_format(
                cr, uid, context=context))

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

        for partner in self.browse(cr, uid, ids, context=context):
            """
            Compose salutation for letters and addresses by applying
            generized prefixes and optional suffix to the display name.
            """
            if partner.use_manual_salutations:
                result[partner.id] = {
                    'salutation': partner.salutation_manual,
                    'salutation_address': partner.salutation_address_manual,
                    }
                continue

            # Use API from partner_firstname
            name = self._prepare_name_custom(
                cr, uid, partner, context=context) or ''
            # Apply prefix/or and suffix
            salutation = get_prefix('salutation', partner) + name
            salutation_address = get_prefix('shortcut', partner) + name
            if partner.title.postnominal:
                salutation += ' ' + partner.title.postnominal
                salutation_address += ' ' + partner.title.postnominal
            result[partner.id] = {
                'salutation': salutation,
                'salutation_address': salutation_address}
        return result

    def on_change_use_manual_salutations(
            self, cr, uid, ids, use_salutation_manual,
            salutation, salutation_address, context=None):
        if not use_salutation_manual:
            return {}
        return {
            'value': {
                'salutation_manual': salutation,
                'salutation_address_manual': salutation_address,
                }}

    _columns = {
        'gender': fields.selection(GENDERS, 'Gender', required=True),
        'salutation': fields.function(
            _get_salutation, multi='salutations',
            type='char', string='Salutation (letter)'),
        'salutation_address': fields.function(
            _get_salutation, multi='salutations',
            type='char', string='Salutation (address)'),
        'use_manual_salutations': fields.boolean(
            'Enter salutations manually'),
        'salutation_manual': fields.char('Manual salutation (letter)'),
        'salutation_address_manual': fields.char(
            'Manual salutation (address)'),
        }

    _defaults = {'gender': 'unknown'}
