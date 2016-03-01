# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
from openerp.tools.translate import _
from stdnum.nl import bsn


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bsn_number = fields.Char("BSN")

    @api.multi
    @api.onchange('bsn_number')
    def onchange_bsn_number(self):
        warning = {}
        for partner in self:
            if partner.bsn_number:
                # properly format the entered BSN
                partner.bsn_number = bsn.format(partner.bsn_number)

                # check is valid, otherwise display a warning
                if not bsn.is_valid(partner.bsn_number):
                    msg = _('The BSN you entered (%s) is not valid.')
                    warning = {
                        'title': _('Warning!'),
                        'message': msg % partner.bsn_number,
                    }

                # search for another partner with the same BSN
                args = [('bsn_number', '=', partner.bsn_number)]
                # refine search in case of multicompany setting
                if partner.company_id:
                    args += [('company_id', '=', partner.company_id.id)]
                partners = self.search(args, limit=1)
                # is another partner exists, display a warning
                if partners:
                    msg = _('Another person (%s) has the same BSN (%s).')
                    warning = {
                        'title': _('Warning!'),
                        'message': msg % (partner.name, partner.bsn_number)
                    }
        return {'warning': warning, }
