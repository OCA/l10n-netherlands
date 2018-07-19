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
