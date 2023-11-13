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
        if self._fields.get(changed_protected_field) and self._fields[
            changed_protected_field
        ].type not in ["many2many", "one2many"]:
            return self[changed_protected_field] == values[changed_protected_field]
        # if field is X2M we must translate commands to values.
        # the only acceptable value is [[6,0,self[changed_protected_field].ids]]
        # wich is what the web client posts in case there is a editable X2M in form
        # that is unchanged.
        return (
            values[changed_protected_field][0] == 6
            and values[changed_protected_field][2] == self[changed_protected_field].ids
        )

    def write(self, values):
        # before doing anything we check the nl_vat_statement:check_state,
        # if this is not allowed it will raise and no further operations
        # are necessary.
        if not self._l10n_nl_vat_statement_should_check_write(values):
            return super().write(values)
        # now we add code to check if any of the modified fields present in
        # values are the same as existing field value. this is a known limitation
        # of odoo web client, it passes all non-readonly value fields in a form
        # for writing , even if the value has not been changed.
        res = True
        protected_fields = self._get_l10n_nl_vat_statement_protected_fields()
        protected_fields_in_values = [x for x in values.keys() if x in protected_fields]
        for this in self:
            # there are protected fields in dict, we proceed to check if such keys
            # are in reality leaving the field the same.
            # we need to recreate this dict every time
            clean_values = dict(values)
            for changed_protected_field in protected_fields_in_values:
                is_equal = this.check_field_is_equal(
                    changed_protected_field, clean_values
                )
                if is_equal:
                    clean_values.pop(changed_protected_field)
            # in case of recordset write we need to evaluate write one by one
            # and re-check that our new clean dict is allowed
            if this._l10n_nl_vat_statement_should_check_write(clean_values):
                if this._l10n_nl_vat_statement_should_check_write(clean_values):
                    this._l10n_nl_vat_statement_check_state()
                res = res and super(AccountMoveLine, this).write(clean_values)
        return res

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
