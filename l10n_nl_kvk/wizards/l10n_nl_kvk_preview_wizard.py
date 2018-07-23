# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class KvKPreviewWizard(models.TransientModel):
    _name = 'l10n.nl.kvk.preview.wizard'

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
            trade_names = target_item['tradeNames']
            partner_name = trade_names.get(
                'businessName'
            ) or trade_names.get(
                'shortBusinessName'
            )
            return partner_name

        def _get_country(first_address):
            country = None
            if first_address.get('country') == 'Nederland':
                country = self.env.ref('base.nl')
            elif first_address.get('country'):
                country = self.env['res.country'].search([
                    ('name', 'ilike', first_address['country'])
                ], limit=1)
            return country

        Handler = self.env['l10n.nl.kvk.api.handler']

        partner_name = _get_partner_name(target_item)

        first_address = target_item.get('addresses', [{}])[0]

        country = _get_country(first_address)

        item = {
            'kvk': target_item['kvkNumber'],
            'name': target_item['kvkNumber'],
            'partner_name': partner_name,
            'country_id': country and country.id or False,
            'partner_city': first_address.get('city'),
            'partner_zip': first_address.get('postalCode'),
        }

        item['partner_street'] = Handler._kvk_format_street(
            first_address.get('street'),
            first_address.get('houseNumber'),
            first_address.get('houseNumberAddition'),
        )

        if target_item.get('websites'):
            item['partner_website'] = target_item['websites'][0]
        return item

    @api.model
    def _get_wizard_lines(self, res_data):

        def _get_entity_type(item_data):
            entity_type = 'headquarters'
            is_legal_person = item_data.get('isLegalPerson')
            if is_legal_person:
                entity_type = 'legal_person'
            return entity_type

        all_lines = []

        if 'apiVersion' not in res_data or 'data' not in res_data:
            return []

        if res_data['apiVersion'] != '2.0':
            return []

        if res_data['data']['totalItems'] == 0:
            return []

        for target_item in res_data['data']['items']:
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
        return super(KvKPreviewWizard, self).create(vals)

    @api.multi
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

    name = fields.Char()
    kvk = fields.Char()
    entity_type = fields.Selection([
        ('legal_person', 'Legal Person'),
        ('headquarters', 'Headquarters')
    ])
    partner_name = fields.Char()
    partner_city = fields.Char()
    country_id = fields.Many2one('res.country', string='Country')
    partner_street = fields.Char()
    partner_zip = fields.Char()
    partner_website = fields.Char()
    partner_vat = fields.Char()

    wizard_id = fields.Many2one('l10n.nl.kvk.preview.wizard', 'Wizard')

    @api.multi
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
