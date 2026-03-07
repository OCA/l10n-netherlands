from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_nl_partner_name_infixes = fields.Char(
        "Partner name infixes",
        config_parameter="l10n_nl_partner_name_infixes",
    )
