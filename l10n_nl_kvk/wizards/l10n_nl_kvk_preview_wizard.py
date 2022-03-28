# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class KvKPreviewWizard(models.TransientModel):
    _name = 'l10n.nl.kvk.preview.wizard'
    _description = 'KvK Preview Wizard'

    name = fields.Char()
    kvk = fields.Char()
    partner_id = fields.Many2one('res.partner', "Partner")
    line_ids = fields.One2many(
        'l10n.nl.kvk.preview.wizard.line',
        'wizard_id',
        'Lines'
    )

    @api.model
    def _get_wizard_lines_values(self, target_item):

        def _get_partner_name(target_item):
            return target_item['handelsnaam']

        def _get_country(target_item):
            country = self.env.ref('base.nl')
            if target_item.get('land') and target_item['land'] != 'Nederland':
                country = self.env['res.country'].search([
                    ('name', 'ilike', target_item['land'])
                ], limit=1)
            return country

        Handler = self.env['l10n.nl.kvk.api.handler']

        partner_name = _get_partner_name(target_item)

        country = _get_country(target_item)

        item = {
            'kvk': target_item['kvkNummer'],
            'name': target_item['kvkNummer'],
            'partner_name': partner_name,
            'country_id': country and country.id or False,
            'partner_city': target_item.get('plaats'),
            'partner_zip': target_item.get('postcode'),
        }

        item['partner_street'] = Handler._kvk_format_street(
            target_item.get('straatnaam'),
            target_item.get('huisnummer'),
            False
        )

        return item

    @api.model
    def _get_wizard_lines(self, res_data):

        def _get_entity_type(item_data):
            if not item_data.get("type"):
                return False
            entity_type_map = {
                'rechtspersoon': "legal_person",
                'hoofdvestiging': "headquarters",
                'nevenvestiging': "branch",
            }
            return entity_type_map[item_data["type"]]

        all_lines = []

        if res_data.get('totaal', 0) == 0:
            return []

        for target_item in res_data['resultaten']:
            item = self._get_wizard_lines_values(target_item)
            item['entity_type'] = _get_entity_type(target_item)
            all_lines.append((0, 0, item), )
        return all_lines

    @api.model
    def _fetch_kvk_partner_data(self, vals):
        Handler = self.env['l10n.nl.kvk.api.handler']
        if 'kvk' in vals:
            url_query = Handler._get_url_query_kvk_api(vals['kvk'])
        elif 'name' in vals:
            url_query = Handler._get_url_query_name_api(vals['name'])

        response = Handler._retrieve_data_by_api(url_query)
        res_data = json.loads(response.decode())
        return self._get_wizard_lines(res_data)

    @api.model
    def create(self, vals):
        vals['line_ids'] = self._fetch_kvk_partner_data(vals)
        return super().create(vals)

    def action_load_partner_values(self):
        self.ensure_one()

        if len(self.line_ids) == 1:
            self.line_ids.set_partner_fields()
            return {}

        return {
            'type': 'ir.actions.act_window',
            'name': self.display_name,
            'views': [(False, 'form')],
            'res_model': 'l10n.nl.kvk.preview.wizard',
            'res_id': self.id,
            'target': 'new'
        }


class KvKPreviewWizardLines(models.TransientModel):
    _name = 'l10n.nl.kvk.preview.wizard.line'
    _description = 'KvK Preview Line Wizard'

    name = fields.Char()
    kvk = fields.Char()
    entity_type = fields.Selection([
        ('legal_person', 'Legal Person'),
        ('headquarters', 'Headquarters'),
        ('branch', 'Branch'),
    ])
    partner_name = fields.Char()
    partner_city = fields.Char()
    country_id = fields.Many2one('res.country', string='Country')
    partner_street = fields.Char()
    partner_zip = fields.Char()
    partner_website = fields.Char()
    partner_vat = fields.Char()

    wizard_id = fields.Many2one('l10n.nl.kvk.preview.wizard', 'Wizard')

    def set_partner_fields(self):
        self.ensure_one()

        self.wizard_id.partner_id.write({
            'name': self.partner_name,
            'city': self.partner_city,
            'zip': self.partner_zip,
            'coc_registration_number': self.kvk,
            'country_id': self.env.ref('base.nl').id,
            'street': self.partner_street,
            'website': self.partner_website,
            'vat': self.partner_vat,
        })
