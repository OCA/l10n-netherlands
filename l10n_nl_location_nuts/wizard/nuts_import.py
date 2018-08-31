# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class NutsImport(models.TransientModel):
    _inherit = 'nuts.import'
    _nl_state_map = {
        'NL13': 'Drenthe',
        'NL23': 'Flevoland',
        'NL12': 'Friesland',
        'NL22': 'Gelderland',
        'NL11': 'Groningen',
        'NL42': 'Limburg',
        'NL41': 'Noord-Brabant',
        'NL32': 'Noord-Holland',
        'NL21': 'Overijssel',
        'NL31': 'Utrecht',
        'NL34': 'Zeeland',
        'NL33': 'Zuid-Holland',
    }

    _nl_state_ids = {
        'Drenthe': 0,
        'Flevoland': 0,
        'Friesland': 0,
        'Gelderland': 0,
        'Groningen': 0,
        'Limburg': 0,
        'Noord-Brabant': 0,
        'Noord-Holland': 0,
        'Overijssel': 0,
        'Utrecht': 0,
        'Zeeland': 0,
        'Zuid-Holland': 0,
    }

    @api.model
    def state_mapping(self, data, node):
        mapping = super(NutsImport, self).state_mapping(data, node)

        # fill map _nl_state_ids with currently used ids
        nl_provinces = self.env['res.country.state'].search([
            ('country_id', '=', self.env.ref('base.nl').id)
        ])
        for province in nl_provinces:
            if province.name in self._nl_state_ids:
                self._nl_state_ids[province.name] = province.id

        # complete the mapping of the state_id with the Dutch provinces
        level = data.get('level', 0)
        code = data.get('code', '')
        if self._current_country.code == 'NL' and level in [3, 4]:
            code_ref = code if level == 3 else code[:-1]
            external_ref = self._nl_state_map.get(code_ref, False)
            if external_ref and self._nl_state_ids[external_ref]:
                mapping['state_id'] = self._nl_state_ids[external_ref]

        return mapping
