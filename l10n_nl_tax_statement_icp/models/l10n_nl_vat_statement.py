# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class VatStatement(models.Model):
    _inherit = "l10n.nl.vat.statement"

    icp_line_ids = fields.One2many(
        "l10n.nl.vat.statement.icp.line",
        "statement_id",
        string="ICP Lines",
        readonly=True,
    )
    icp_total = fields.Monetary(
        string="Total ICP amount",
        compute="_compute_icp_total",
        help="Total amount in currency of the statement.",
    )

    @api.depends("icp_line_ids.amount_products", "icp_line_ids.amount_services")
    def _compute_icp_total(self):
        for statement in self:
            amount_products = statement.icp_line_ids.mapped("amount_products")
            amount_services = statement.icp_line_ids.mapped("amount_services")
            statement.icp_total = sum(amount_products) + sum(amount_services)

    def _create_icp_lines(self):
        """Computes ICP lines for the report"""
        for statement in self:
            statement.icp_line_ids.unlink()
            icp_line_vals = statement._prepare_icp_lines()
            self.env["l10n.nl.vat.statement.icp.line"].create(icp_line_vals)

    @api.model
    def _prepare_icp_lines(self):
        """Prepares an internal data structure representing the ICP lines"""
        self.ensure_one()
        amounts_map = self._get_partner_amounts_map()
        icp_line_vals = []
        for partner_id in amounts_map:
            icp_line_vals.append(
                {
                    "country_code": amounts_map[partner_id]["country_code"],
                    "vat": amounts_map[partner_id]["vat"],
                    "amount_products": amounts_map[partner_id]["amount_products"],
                    "amount_services": amounts_map[partner_id]["amount_services"],
                    "currency_id": amounts_map[partner_id]["currency_id"],
                    "partner_id": partner_id,
                    "statement_id": self.id,
                }
            )
        return icp_line_vals

    def _is_3b_omzet_line(self, line):
        if line.tax_tag_ids.filtered(lambda t: "3b" in t.name):
            if line.product_id and line.product_id.type != "service":
                return True
            if not line.product_id and line.tax_ids.filtered(
                lambda t: "dienst" not in t.name
            ):
                return True
        return False

    def _is_3b_omzet_diensten_line(self, line):
        if line.tax_tag_ids.filtered(lambda t: "3b" in t.name):
            if line.product_id and line.product_id.type == "service":
                return True
            if not line.product_id and line.tax_ids.filtered(
                lambda t: "dienst" in t.name
            ):
                return True
        return False

    def _get_partner_amounts_map(self):
        """Generate an internal data structure representing the ICP lines"""
        self.ensure_one()

        partner_amounts_map = {}
        move_lines = self._get_all_statement_move_lines()
        if not move_lines and self.sudo().parent_id:
            move_lines = self.sudo().parent_id._get_all_statement_move_lines()
        move_lines = move_lines.sudo().filtered(
            lambda l: l.company_id == self.company_id
        )
        for line in move_lines:
            is_3b_omzet = self._is_3b_omzet_line(line)
            is_3b_omzet_diensten = self._is_3b_omzet_diensten_line(line)
            if is_3b_omzet or is_3b_omzet_diensten:
                vals = self._prepare_icp_line_from_move_line(line)
                if vals["partner_id"] not in partner_amounts_map:
                    self._init_partner_amounts_map(partner_amounts_map, vals)
                self._update_partner_amounts_map(partner_amounts_map, vals)
        return partner_amounts_map

    @classmethod
    def _update_partner_amounts_map(cls, partner_amounts_map, vals):
        """Update amounts of the internal ICP lines data structure"""
        map_data = partner_amounts_map[vals["partner_id"]]
        map_data["amount_products"] += vals["amount_products"]
        map_data["amount_services"] += vals["amount_services"]

    @classmethod
    def _init_partner_amounts_map(cls, partner_amounts_map, vals):
        """Initialize the internal ICP lines data structure"""
        partner_amounts_map[vals["partner_id"]] = {
            "country_code": vals["country_code"],
            "vat": vals["vat"],
            "currency_id": vals["currency_id"],
            "amount_products": 0.0,
            "amount_services": 0.0,
        }

    def _prepare_icp_line_from_move_line(self, line):
        """Gets move line details and prepares ICP report line data"""
        self.ensure_one()

        balance = line.balance and -line.balance or 0
        if line.company_currency_id != self.currency_id:
            balance = line.company_currency_id._convert(
                balance, self.currency_id, self.company_id, line.date
            )
        amount_products = balance
        amount_services = 0.0
        if self._is_3b_omzet_diensten_line(line):
            amount_products = 0.0
            amount_services = balance

        return {
            "partner_id": line.partner_id.id,
            "country_code": line.partner_id.country_id.code,
            "vat": line.partner_id.vat,
            "amount_products": amount_products,
            "amount_services": amount_services,
            "currency_id": self.currency_id.id,
        }

    def reset(self):
        """Removes ICP lines if reset to draft"""
        self.mapped("icp_line_ids").unlink()
        return super().reset()

    def post(self):
        """Checks configuration when validating the statement"""
        self.ensure_one()
        res = super().post()
        self._create_icp_lines()
        return res

    @api.model
    def _modifiable_values_when_posted(self):
        """Returns the modifiable fields even when the statement is posted"""
        res = super()._modifiable_values_when_posted()
        res.append("icp_line_ids")
        res.append("icp_total")
        return res

    def icp_update(self):
        """Update button"""
        self.ensure_one()

        if self.state in ["final"]:
            raise UserError(_("You cannot modify a final statement!"))

        # recreate lines
        self._create_icp_lines()
