# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_nl_vat_statement_id = fields.Many2one(
        related="move_id.l10n_nl_vat_statement_id",
        store=True,
        string="Related Move Statement",
    )
    l10n_nl_vat_statement_include = fields.Boolean(
        related="move_id.l10n_nl_vat_statement_include",
        store=True,
    )

    @api.model
    def _get_l10n_nl_vat_statement_protected_fields(self):
        """ Hook for extensions """
        return [
            "date",
            "debit",
            "credit",
            "balance",
            "tax_ids",
            "l10n_nl_vat_statement_include",
            "tax_tag_ids",
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
                        "You cannot modify a Journal Item in a posted/final "
                        "tax statement: %s"
                    )
                    % (line.l10n_nl_vat_statement_id.name,)
                )
