# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_nl_vat_statement_id = fields.Many2one("l10n.nl.vat.statement", copy=False)
    l10n_nl_vat_statement_include = fields.Boolean(
        "Include in VAT Statement", copy=False
    )

    def l10n_nl_add_move_in_statement(self):
        self.write({"l10n_nl_vat_statement_include": True})

    def l10n_nl_unlink_move_from_statement(self):
        self.write({"l10n_nl_vat_statement_include": False})

    @api.model
    def _get_l10n_nl_vat_statement_protected_fields(self):
        """ Hook for extensions """
        return [
            "date",
            "invoice_date",
            "l10n_nl_vat_statement_include",
        ]

    def write(self, values):
        if self._l10n_nl_vat_statement_should_check_write(values):
            self._l10n_nl_vat_statement_check_state()
        return super().write(values)

    @api.model
    def _l10n_nl_vat_statement_should_check_write(self, values):
        """ Hook for extensions """
        all_fields = set(values.keys())
        protected_fields = set(self._get_l10n_nl_vat_statement_protected_fields())
        return bool(protected_fields & all_fields)

    def _l10n_nl_vat_statement_check_state(self):
        if self.env.context.get("skip_check_state"):
            return
        for line in self.filtered("l10n_nl_vat_statement_id"):
            if line.l10n_nl_vat_statement_id.state != "draft":
                raise UserError(
                    _(
                        "You cannot modify a Journal Entry in a posted/final "
                        "tax statement: %s"
                    )
                    % (line.l10n_nl_vat_statement_id.name,)
                )
