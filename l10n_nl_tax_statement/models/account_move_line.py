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
        """Hook for extensions"""
        return [
            "date",
            "debit",
            "credit",
            "balance",
            "tax_ids",
            "l10n_nl_vat_statement_include",
            "tax_tag_ids",
        ]

    def check_field_is_equal(self, changed_protected_field, values):
        self.ensure_one()
        field = self._fields.get(changed_protected_field)
        old_value = self[changed_protected_field]
        new_value = values[changed_protected_field]
        if field.type in ["many2many", "one2many"]:
            if all(isinstance(_id, int) for _id in new_value):
                return new_value == old_value.ids
            # if field is X2M , the only other acceptable value is
            # [[6,0,self[changed_protected_field].ids]]
            # wich is what the web client posts in case there is a editable X2M in form
            # that is unchanged.
            # If it is a list of tuple-commands, and the last one is precisely
            # values[changed_protected_field][2] == self[changed_protected_field].ids
            # we will not accept any modification to protected fields,
            # only the standard 6,0,[ids] coming from the default web edit.
            return (
                len(new_value) == 1
                and new_value[0][0] == 6
                and new_value[0][2] == old_value.ids
            )
        if new_value:
            return old_value == new_value
        return bool(old_value) == bool(new_value)

    def write(self, values):
        # before doing anything we check the nl_vat_statement:check_state,
        if not self._l10n_nl_vat_statement_should_check_write(values):
            return super().write(values)
        # now we add code to check if any of the modified fields present in
        # values are the same as existing field value. this is a known limitation
        # of odoo web client, it passes all non-readonly value fields in a form
        # for writing , even if the value has not been changed.
        protected_fields = self._get_l10n_nl_vat_statement_protected_fields()
        protected_fields_in_values = [x for x in values.keys() if x in protected_fields]
        invalid_fields = set()
        for this in self:
            for protected_field in protected_fields_in_values:
                is_equal = this.check_field_is_equal(protected_field, values)
                if not is_equal:
                    # if the field is invalid in even one
                    # of the records it cannot be popped
                    invalid_fields.add(protected_field)
        for protected_field in protected_fields_in_values:
            if protected_field not in invalid_fields:
                values.pop(protected_field)
        if self._l10n_nl_vat_statement_should_check_write(values):
            for this in self:
                this._l10n_nl_vat_statement_check_state()
        return super().write(values)

    @api.model
    def _l10n_nl_vat_statement_should_check_write(self, values):
        """Hook for extensions"""
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
