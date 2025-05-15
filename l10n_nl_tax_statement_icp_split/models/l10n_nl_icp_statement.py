# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import is_leaf


class L10nNlIcpStatement(models.Model):
    _inherit = "l10n.nl.vat.statement"
    _name = "l10n.nl.icp.statement"

    name = fields.Char("ICP statement")
    line_ids = fields.One2many(inverse_name="icp_statement_id")
    icp_line_ids = fields.One2many(inverse_name="icp_statement_id")
    move_line_ids = fields.One2many(inverse_name="l10n_nl_icp_statement_id")
    icp_line_ids_has_errors = fields.Boolean(compute="_compute_icp_line_ids_has_errors")

    @api.depends("icp_line_ids.error")
    def _compute_icp_line_ids_has_errors(self):
        for this in self:
            this.icp_line_ids_has_errors = any(this.icp_line_ids.mapped("error"))

    def _init_move_line_domain(self):
        result = super()._init_move_line_domain()
        return [
            ("l10n_nl_icp_statement_id", leaf[1], leaf[2])
            if is_leaf(leaf) and leaf[0] == "l10n_nl_vat_statement_id"
            else leaf
            for leaf in result
        ]

    def statement_update(self):
        result = super().statement_update()
        self.icp_update()
        return result

    def _prepare_icp_lines(self):
        result = super()._prepare_icp_lines()
        IcpLine = self.env["l10n.nl.vat.statement.icp.line"]
        partner_amounts_map = self._get_partner_amounts_map()
        for vals in result:
            vals["icp_statement_id"] = vals.pop("statement_id")
            record = IcpLine.new(vals)
            try:
                record._check_country_code()
            except ValidationError as error:
                vals["error"] = ",".join(error.args)
            if not record.partner_id:
                vals["error"] = _("No partner set")
            vals["move_line_ids"] = list(
                partner_amounts_map[vals["partner_id"]]["move_line_ids"]
            )
        return result

    def _prepare_icp_line_from_move_line(self, line):
        result = super()._prepare_icp_line_from_move_line(line)
        result["move_line_ids"] = set(line.ids)
        return result

    @classmethod
    def _init_partner_amounts_map(cls, partner_amounts_map, vals):
        result = super()._init_partner_amounts_map(partner_amounts_map, vals)
        partner_amounts_map[vals["partner_id"]]["move_line_ids"] = vals["move_line_ids"]
        return result

    @classmethod
    def _update_partner_amounts_map(cls, partner_amounts_map, vals):
        result = super()._update_partner_amounts_map(partner_amounts_map, vals)
        partner_amounts_map[vals["partner_id"]]["move_line_ids"].union(
            vals["move_line_ids"]
        )
        return result

    def post(self):
        return super(
            L10nNlIcpStatement, self.with_context(l10n_nl_icp_statement=True)
        ).post()

    def reset(self):
        execute_org = self.env.cr.execute

        def execute(query, *args):
            return execute_org(
                query.replace("l10n_nl_vat_statement_id", "l10n_nl_icp_statement_id"),
                *args
            )

        self.env.cr.execute = execute

        try:
            result = super().reset()
        finally:
            self.env.cr.execute = execute_org
        return result
