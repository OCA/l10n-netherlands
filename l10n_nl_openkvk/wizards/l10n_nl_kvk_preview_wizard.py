# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo import api, fields, models

MAP_RESULT_KEY_OPENKVK = {
    'id': 'line_id_str',
    'handelsnaam': 'partner_name',
    'dossiernummer': 'kvk',
    'plaats': 'partner_city',
    'link': 'link',
    'text': 'name',
}


class KvKPreviewWizard(models.TransientModel):
    _inherit = 'l10n.nl.kvk.preview.wizard'

    @api.model
    def _get_wizard_lines_openkvk(self, res_data):
        def _map_item(item_key):
            if item_key in MAP_RESULT_KEY_OPENKVK:
                item_key = MAP_RESULT_KEY_OPENKVK[item_key]
            else:
                item_key = 'extra'
            return item_key

        def _get_entity_type(item_data):
            entity_type = False
            if item_data.startswith('hoofdvestiging-'):
                entity_type = 'headquarters'
            elif item_data.startswith('rechtspersoon-'):
                entity_type = 'legal_person'
            return entity_type

        all_lines = []
        all_kvk = res_data.get('dossiernummer', [])
        all_names = res_data.get('handelsnaam', [])
        for record in all_kvk + all_names:
            item = {}
            for item_key, item_data in record.items():
                item_key = _map_item(item_key)
                if item_key == 'line_id_str':
                    entity_type_data = _get_entity_type(item_data)
                    item.update({'entity_type': entity_type_data})
                item.update({item_key: item_data})
            all_lines.append((0, 0, item), )
        return all_lines

    @api.model
    def _get_wizard_lines(self, res_data):
        Handler = self.env['l10n.nl.kvk.api.handler']
        if Handler._get_config('service') != 'openkvk':
            return super()._get_wizard_lines(res_data)

        return self._get_wizard_lines_openkvk(res_data)


class KvKPreviewWizardLines(models.TransientModel):
    _inherit = 'l10n.nl.kvk.preview.wizard.line'

    link = fields.Char()
    line_id_str = fields.Char()
    extra = fields.Char()

    def _retrieve_partner_data_by_openkvk_api(self):
        self.ensure_one()

        url_search = 'https://api.overheid.io/openkvk/{0}'
        url_query = url_search.format(self.line_id_str)

        Handler = self.env['l10n.nl.kvk.api.handler']
        response = Handler._retrieve_data_by_api(url_query)

        return json.loads(response.decode())

    def set_partner_fields(self):
        Handler = self.env['l10n.nl.kvk.api.handler']
        if Handler._get_config('service') == 'openkvk':
            res_data = self._retrieve_partner_data_by_openkvk_api()

            Handler = self.env['l10n.nl.kvk.api.handler']
            street = Handler._kvk_format_street(
                res_data.get('straat'),
                res_data.get('huisnummer'),
                res_data.get('huisnummertoevoeging')
            )
            self.write({
                'name': res_data['handelsnaam'],
                'partner_name': res_data['handelsnaam'],
                'kvk': res_data['dossiernummer'],
                'country_id': self.env.ref('base.nl').id,
                'partner_city': res_data.get('plaats'),
                'partner_street': street,
                'partner_zip': res_data.get('postcode'),
                'partner_vat': res_data.get('BTW'),
            })

        return super().set_partner_fields()
