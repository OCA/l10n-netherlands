from openerp.osv import orm, fields


class Title(orm.Model):
    _inherit = 'res.partner.title'
    _columns = {
        'salutation_male': fields.char(
            'Salutation male'),
        'salutation_female': fields.char(
            'Salutation female'),
        'shortcut_male': fields.char(
            'Shortcut male'),
        'shortcut_female': fields.char(
            'Shortcut female'),
        'postnominal': fields.char('Postnominal'),
        }
