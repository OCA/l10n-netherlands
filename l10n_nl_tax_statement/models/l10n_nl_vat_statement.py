# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang


class VatStatement(models.Model):
    _name = "l10n.nl.vat.statement"
    _description = "Netherlands Vat Statement"

    name = fields.Char(
        string="Tax Statement",
        required=True,
        compute="_compute_name",
        store=True,
        readonly=False,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted"), ("final", "Final")],
        readonly=True,
        default="draft",
        copy=False,
        string="Status",
    )
    line_ids = fields.One2many("l10n.nl.vat.statement.line", "statement_id", "Lines")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    from_date = fields.Date(
        required=True, store=True, readonly=False, compute="_compute_date_range"
    )
    to_date = fields.Date(
        required=True, store=True, readonly=False, compute="_compute_date_range"
    )
    date_range_id = fields.Many2one("date.range", "Date range")
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")
    date_posted = fields.Datetime(readonly=True)
    date_update = fields.Datetime(readonly=True)

    btw_total = fields.Monetary(
        compute="_compute_btw_total", string="5g. Total (5c + 5d)"
    )
    format_btw_total = fields.Char(
        compute="_compute_amount_format_btw_total", string="5g - Total"
    )
    move_line_ids = fields.One2many(
        "account.move.line",
        "l10n_nl_vat_statement_id",
        string="Entry Lines",
        readonly=True,
    )
    multicompany_fiscal_unit = fields.Boolean()
    display_multicompany_fiscal_unit = fields.Boolean(
        compute="_compute_display_multicompany_fiscal_unit"
    )
    fiscal_unit_company_ids = fields.Many2many("res.company")
    parent_id = fields.Many2one(
        "l10n.nl.vat.statement",
        "Parent Statement",
        compute="_compute_parent_statement_id",
    )
    display_button_add_all_undeclared_invoices = fields.Boolean(
        compute="_compute_display_button_add_all_undeclared_invoices",
    )

    @api.depends(
        "unreported_move_from_date",
        "company_id",
        "is_invoice_basis",
        "from_date",
        "to_date",
    )
    def _compute_unreported_move_ids(self):
        for statement in self:
            domain = statement._get_unreported_move_domain()
            move_lines = self.env["account.move.line"].search(domain)
            moves = move_lines.mapped("move_id").sorted("date")
            statement.unreported_move_ids = moves

    def _search_unreported_move_ids(self, operator, value):
        if operator == "in":
            return [("id", operator, value)]
        else:
            raise ValueError(_("Unreported moves: unsupported search operator"))

    @api.depends(
        "company_id",
        "company_id.child_ids",
        "company_id.currency_id",
        "company_id.country_id",
    )
    def _compute_display_multicompany_fiscal_unit(self):
        for statement in self:
            is_fiscal_entity = True
            child_ids = statement.company_id.child_ids
            if not child_ids:
                is_fiscal_entity = False
            currency = statement.company_id.currency_id
            nl_country = self.env.ref("base.nl")
            if all(c.currency_id != currency for c in child_ids):
                is_fiscal_entity = False
            if all(c.partner_id.country_id != nl_country for c in child_ids):
                is_fiscal_entity = False
            statement.display_multicompany_fiscal_unit = is_fiscal_entity

    @api.depends("company_id", "from_date", "to_date")
    def _compute_parent_statement_id(self):
        for statement in self:
            statement.parent_id = False
            if statement.company_id.parent_id:
                parent = self.sudo().search(
                    [
                        ("fiscal_unit_company_ids", "=", statement.company_id.id),
                        ("company_id", "!=", statement.company_id.id),
                        ("from_date", "=", statement.from_date),
                        ("to_date", "=", statement.to_date),
                    ]
                )
                statement.parent_id = parent

    def _init_move_line_domain(self):
        return [
            ("company_id", "in", self._get_company_ids_full_list()),
            ("l10n_nl_vat_statement_id", "=", False),
            ("parent_state", "=", "posted"),
            "|",
            ("tax_ids", "!=", False),
            ("tax_line_id", "!=", False),
        ]

    def _get_unreported_move_domain(self):
        self.ensure_one()
        domain = self._init_move_line_domain()
        if self.is_invoice_basis and not self.unreported_move_from_date:
            domain += [
                "|",
                "&",
                ("move_id.invoice_date", "=", False),
                ("date", "<", self.from_date),
                "&",
                ("move_id.invoice_date", "!=", False),
                ("move_id.invoice_date", "<", self.from_date),
            ]
        elif self.is_invoice_basis and self.unreported_move_from_date:
            domain += [
                "|",
                "&",
                "&",
                ("move_id.invoice_date", "=", False),
                ("date", "<", self.from_date),
                ("date", ">=", self.unreported_move_from_date),
                "&",
                "&",
                ("move_id.invoice_date", "!=", False),
                ("move_id.invoice_date", "<", self.from_date),
                ("move_id.invoice_date", ">=", self.unreported_move_from_date),
            ]
        else:
            domain += [("date", "<", self.from_date)]
            if self.unreported_move_from_date:
                domain += [("date", ">=", self.unreported_move_from_date)]
        return domain

    def _get_company_ids_full_list(self):
        self.ensure_one()
        company_ids = [self.company_id.id]
        if self.multicompany_fiscal_unit:
            company_ids += self.fiscal_unit_company_ids.ids
        return company_ids

    unreported_move_ids = fields.One2many(
        "account.move",
        string="Unreported Journal Entries",
        compute="_compute_unreported_move_ids",
        search="_search_unreported_move_ids",
    )
    unreported_move_from_date = fields.Date(
        compute="_compute_unreported_move_from_date", store=True, readonly=False
    )
    is_invoice_basis = fields.Boolean(
        string="NL Tax Invoice Basis", related="company_id.l10n_nl_tax_invoice_basis"
    )

    @api.depends("btw_total")
    def _compute_amount_format_btw_total(self):
        for statement in self:
            btw = formatLang(self.env, statement.btw_total, monetary=True)
            statement.format_btw_total = btw

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        fy_dates = self.env.company.compute_fiscalyear_dates(datetime.now())
        defaults.setdefault("from_date", fy_dates["date_from"])
        defaults.setdefault("to_date", fy_dates["date_to"])
        defaults.setdefault("name", self.env.company.name)
        return defaults

    @api.depends("date_range_id")
    def _compute_date_range(self):
        for statement in self:
            if statement.date_range_id and statement.state == "draft":
                statement.from_date = statement.date_range_id.date_start
                statement.to_date = statement.date_range_id.date_end
            statement.from_date = statement.from_date
            statement.to_date = statement.to_date

    @api.depends("from_date", "to_date")
    def _compute_name(self):
        for statement in self:
            display_name = statement.company_id.name
            if statement.from_date and statement.to_date:
                from_date = fields.Date.to_string(statement.from_date)
                to_date = fields.Date.to_string(statement.to_date)
                display_name += ": " + " ".join([from_date, to_date])
            statement.name = display_name

    @api.depends("from_date")
    def _compute_unreported_move_from_date(self):
        # by default the unreported_move_from_date is set to
        # a quarter (three months) before the from_date of the statement
        for statement in self:
            date_from = (
                statement.from_date + relativedelta(months=-3, day=1)
                if statement.from_date
                else False
            )
            statement.unreported_move_from_date = date_from

    def _prepare_lines(self):
        lines = {}
        lines["1"] = {"code": "1", "name": _("Leveringen en/of diensten binnenland")}
        lines["1a"] = {
            "code": "1a",
            "omzet": 0.0,
            "btw": 0.0,
            "name": _("Leveringen/diensten belast met hoog tarief"),
        }
        lines["1b"] = {
            "code": "1b",
            "omzet": 0.0,
            "btw": 0.0,
            "name": _("Leveringen/diensten belast met laag tarief"),
        }
        lines["1c"] = {
            "code": "1c",
            "omzet": 0.0,
            "btw": 0.0,
            "name": _("Leveringen/diensten belast met overige tarieven " "behalve 0%"),
        }
        lines["1d"] = {
            "code": "1d",
            "omzet": 0.0,
            "btw": 0.0,
            "name": _("1d Prive-gebruik"),
        }
        lines["1e"] = {
            "code": "1e",
            "omzet": 0.0,
            "name": _("Leveringen/diensten belast met 0%"),
        }
        lines["2"] = {
            "code": "2",
            "name": _("Verleggingsregelingen: BTW naar u verlegd"),
        }
        lines["2a"] = {
            "code": "2a",
            "omzet": 0.0,
            "btw": 0.0,
            "name": _("Heffing van omzetbelasting is naar u verlegd"),
        }
        lines["3"] = {"code": "3", "name": _("Leveringen naar het buitenland")}
        lines["3a"] = {
            "code": "3a",
            "omzet": 0.0,
            "name": _("Leveringen naar landen buiten de EU"),
        }
        lines["3b"] = {
            "code": "3b",
            "omzet": 0.0,
            "name": _("Leveringen naar landen binnen de EU"),
        }
        lines["3c"] = {
            "code": "3c",
            "omzet": 0.0,
            "name": _("Installatie/afstandsverkopen binnen de EU"),
        }
        lines["4"] = {"code": "4", "name": _("Leveringen vanuit het buitenland")}
        lines["4a"] = {
            "code": "4a",
            "omzet": 0.0,
            "btw": 0.0,
            "name": _("Verwerving uit landen buiten de EU"),
        }
        lines["4b"] = {
            "code": "4b",
            "omzet": 0.0,
            "btw": 0.0,
            "name": _("Verwerving van goederen uit landen binnen de EU"),
        }
        lines["5"] = {"code": "5", "name": _("Voorbelasting")}
        lines["5a"] = {
            "code": "5a",
            "btw": 0.0,
            "name": _("Verschuldigde omzetbelasting (rubrieken 1a t/m 4b)"),
        }
        lines["5b"] = {"code": "5b", "btw": 0.0, "name": _("Voorbelasting")}
        lines["5c"] = {
            "code": "5c",
            "btw": 0.0,
            "name": _("Subtotaal (rubriek 5a min 5b)"),
        }
        lines["5d"] = {
            "code": "5d",
            "btw": 0.0,
            "name": _("Vermindering volgens de kleineondernemersregeling"),
        }
        lines["5e"] = {
            "code": "5e",
            "btw": 0.0,
            "name": _("Schatting vorige aangifte(n)"),
        }
        lines["5f"] = {"code": "5f", "btw": 0.0, "name": _("Schatting deze aangifte")}
        return lines

    def _finalize_lines(self, lines):
        _1ab = lines["1a"]["btw"]
        _1bb = lines["1b"]["btw"]
        _1cb = lines["1c"]["btw"]
        _1db = lines["1d"]["btw"]
        _2ab = lines["2a"]["btw"]
        _4ab = lines["4a"]["btw"]
        _4bb = lines["4b"]["btw"]

        # 5a is the sum of 1a through 4b
        _5ab = _1ab + _1bb + _1cb + _1db + _2ab + _4ab + _4bb

        # 5b: invert the original sign (5b should be always positive)
        lines["5b"]["btw"] = lines["5b"]["btw"] * -1
        _5bb = lines["5b"]["btw"]

        # 5c is the difference: 5a - 5b
        _5cb = _5ab - _5bb

        # update 5a and 5c
        lines["5a"].update({"btw": _5ab})
        lines["5c"].update({"btw": _5cb})

        # omzet (from 1a to 4b): invert the original sign
        # in case it differs from the sign of related btw
        to_be_checked_inverted = ["1a", "1b", "1c", "1d", "2a", "4a", "4b"]
        for code in to_be_checked_inverted:
            btw_sign = 1 if lines[code]["btw"] >= 0.0 else -1
            omzet_sign = 1 if lines[code]["omzet"] >= 0.0 else -1
            if btw_sign != omzet_sign:
                lines[code]["omzet"] *= -1

        return lines

    def _get_tags_map(self):
        country_nl = self.env.ref("base.nl")
        nl_tags = self.env["account.account.tag"].search(
            [("country_id", "=", country_nl.id), ("applicability", "=", "taxes")]
        )
        if not nl_tags:
            raise UserError(
                _(
                    "Tags mapping not configured for The Netherlands! "
                    "Check the NL BTW Tags Configuration."
                )
            )
        pattern_code = re.compile(r"[+,-]?\d\w")
        matching = {}
        for tag in nl_tags:
            res_code = pattern_code.match(tag.name)
            if re.search("omzet", tag.name, re.IGNORECASE):
                matching.update({tag.id: (res_code.group(0), "omzet")})
            elif re.search("btw", tag.name, re.IGNORECASE):
                matching.update({tag.id: (res_code.group(0), "btw")})
            elif res_code:
                matching.update({tag.id: (res_code.group(0), False)})
        return matching

    def statement_update(self):
        self.ensure_one()

        if self.state in ["posted", "final"]:
            raise UserError(_("You cannot modify a posted statement!"))

        if self.parent_id:
            return

        # clean old lines
        self.line_ids.unlink()

        # calculate lines
        lines = self._prepare_lines()
        move_lines = self._compute_move_lines()
        self._set_statement_lines(lines, move_lines)
        move_lines = self._compute_past_invoices_move_lines()
        self._set_statement_lines(lines, move_lines)
        self._finalize_lines(lines)

        # create lines
        self.write(
            {
                "line_ids": [(0, 0, line) for line in lines.values()],
                "date_update": fields.Datetime.now(),
            }
        )

    def _compute_past_invoices_move_lines(self):
        self.ensure_one()
        moves_to_include = self.unreported_move_ids.filtered(
            lambda m: m.l10n_nl_vat_statement_include
        )
        return moves_to_include.line_ids

    def _compute_move_lines(self):
        self.ensure_one()
        domain = self._get_move_lines_domain()
        return self.env["account.move.line"].search(domain)

    def _set_statement_lines(self, lines, move_lines):
        self.ensure_one()
        tags_map = self._get_tags_map()
        for line in move_lines:
            for tag in line.tax_tag_ids:
                tag_map = tags_map.get(tag.id)
                if tag_map:
                    code, column = tag_map
                    code = self._strip_sign_in_tag_code(code)
                    if not column:
                        if "tax" in lines[code]:
                            column = "tax"
                        else:
                            column = "base"
                    lines[code][column] -= line.balance

    def finalize(self):
        self.ensure_one()
        self.write({"state": "final"})

    def _check_prev_open_statements(self):
        self.ensure_one()
        domain = self._domain_check_prev_open_statements()
        prev_open_statements = self.search(domain, limit=1)

        if prev_open_statements:
            raise UserError(
                _(
                    "You cannot post a statement if all the previous "
                    "statements are not yet posted! "
                    "Please Post all the other statements first."
                )
            )

    def _domain_check_prev_open_statements(self):
        self.ensure_one()
        return [
            ("company_id", "=", self.company_id.id),
            ("state", "=", "draft"),
            ("id", "<", self.id),
        ]

    def post(self):
        self.ensure_one()
        self._check_prev_open_statements()

        self.write({"state": "posted", "date_posted": fields.Datetime.now()})
        self.unreported_move_ids.filtered(
            lambda m: m.l10n_nl_vat_statement_include
        ).write({"l10n_nl_vat_statement_id": self.id})
        self.unreported_move_ids.flush()
        move_lines = self._compute_move_lines()
        move_lines.move_id.write({"l10n_nl_vat_statement_id": self.id})
        move_lines.move_id.flush()

    def _get_move_lines_domain(self):
        domain = self._init_move_line_domain()
        if self.is_invoice_basis:
            domain += [
                "|",
                "&",
                "&",
                ("move_id.invoice_date", "=", False),
                ("date", "<=", self.to_date),
                ("date", ">=", self.from_date),
                "&",
                "&",
                ("move_id.invoice_date", "!=", False),
                ("move_id.invoice_date", "<=", self.to_date),
                ("move_id.invoice_date", ">=", self.from_date),
            ]
        else:
            domain += [("date", "<=", self.to_date), ("date", ">=", self.from_date)]
        return domain

    def reset(self):
        self.write({"state": "draft", "date_posted": None})
        req = """
            UPDATE account_move_line
            SET l10n_nl_vat_statement_id = NULL
            WHERE
              l10n_nl_vat_statement_id = %s
        """
        self.env.cr.execute(req, (self.id,))

    def _modifiable_values_when_posted(self):
        return ["state"]

    def write(self, values):
        for statement in self:
            if statement.state == "final":
                raise UserError(_("You cannot modify a statement set as final!"))
            if "state" not in values or values["state"] != "draft":
                if statement.state == "posted":
                    for val in values:
                        if val not in self._modifiable_values_when_posted():
                            raise UserError(
                                _(
                                    "You cannot modify a posted statement! "
                                    "Reset the statement to draft first."
                                )
                            )
        return super().write(values)

    def unlink(self):
        for statement in self:
            if statement.state == "posted":
                raise UserError(
                    _(
                        "You cannot delete a posted statement! "
                        "Reset the statement to draft first."
                    )
                )
            if statement.state == "final":
                raise UserError(_("You cannot delete a statement set as final!"))
        super().unlink()

    @api.depends("line_ids.btw")
    def _compute_btw_total(self):
        for statement in self:
            lines = statement.line_ids
            total_lines = lines.filtered(lambda l: l.code in ["5c", "5d"])
            statement.btw_total = sum(line.btw for line in total_lines)

    @api.constrains("fiscal_unit_company_ids")
    def _check_fiscal_unit_company_ids(self):
        for statement in self.sudo():
            unit_companies = statement.fiscal_unit_company_ids
            country_nl = self.env.ref("base.nl")
            if any(u.country_id != country_nl for u in unit_companies):
                raise ValidationError(
                    _(
                        "The Companies belonging to a fiscal unit "
                        "must be in The Netherlands."
                    )
                )

    def _get_all_statement_move_lines(self):
        self.ensure_one()
        if self.state == "draft":
            curr_amls = self._compute_move_lines()
            past_amls = self._compute_past_invoices_move_lines()
            all_amls = curr_amls | past_amls
        else:
            all_amls = self.move_line_ids
        return all_amls

    @api.model
    def _strip_sign_in_tag_code(self, code):
        if code[0:1] in ["+", "-"]:
            code = code[1:]
        return code

    def add_all_undeclared_invoices(self):
        self.ensure_one()
        self.unreported_move_ids.l10n_nl_add_move_in_statement()

    @api.depends("unreported_move_ids.l10n_nl_vat_statement_include")
    def _compute_display_button_add_all_undeclared_invoices(self):
        for statement in self:
            has_unreported = any(
                not move.l10n_nl_vat_statement_include
                for move in statement.unreported_move_ids
            )
            is_draft = statement.state == "draft"
            statement.display_button_add_all_undeclared_invoices = (
                is_draft and has_unreported
            )
