# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from mako.template import Template
from odoo import models, fields, api


class ResPartner(models.Model):
    """Extend res.partner with extra fields for Dutch names."""
    _inherit = 'res.partner'

    initials = fields.Char()
    infix = fields.Char()

    @api.multi
    @api.depends("firstname", "lastname", "initials", "infix")
    def _compute_name(self):
        for record in self:
            record.name = record._get_computed_name(
                record.lastname, record.firstname, record.initials,
                record.infix)

    @api.onchange("firstname", "lastname", "initials", "infix")
    def _onchange_subnames(self):
        return super(ResPartner, self)._onchange_subnames()

    @api.model
    def _get_computed_name(self, lastname, firstname, initials=None,
                           infix=None):
        name_template = Template(
            self.env.context.get(
                'name_format',
                "${firstname or initials or ''}"
                "${(firstname or initials) and ' ' or ''}"
                "${infix or ''}${infix and ' ' or ''}${lastname or ''}"))
        name = name_template.render(**{
            'firstname': firstname,
            'lastname': lastname,
            'initials': initials,
            'infix': infix,
        })
        return name if name else ''

    @api.model
    def _get_inverse_name(self, name, is_company=False):
        result = super(ResPartner, self)._get_inverse_name(
            name, is_company=is_company)
        # super assumes $lastname $firstname, we want it the other way around
        return dict(
            result, lastname=result['firstname'], firstname=result['lastname'])
