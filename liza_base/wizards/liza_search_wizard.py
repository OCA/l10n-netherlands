# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, exceptions, fields, models

from ..liza_const import (
    ALLOWED_COUNTRY_CODES,
    ALLOWED_COUNTRY_SELECTION,
    COUNTRY_CODE_BELGIUM,
    SEARCH_RESULT_KEYS,
)


class LizaBaseSearchWizard(models.TransientModel):
    _name = "liza.search.wizard"
    _description = "Liza Search Wizard"

    partner_id = fields.Many2one("res.partner", required=True, ondelete="cascade")

    vat = fields.Char("VAT")
    company_registry = fields.Char("Company ID")
    search_term = fields.Char()
    zip = fields.Char("ZIP Code")
    city = fields.Char()
    country_code = fields.Selection(
        ALLOWED_COUNTRY_SELECTION,
        "Country",
    )

    display_search_button = fields.Boolean(default=True, readonly=True)
    line_ids = fields.One2many("liza.search.wizard.line", "wizard_id", "Search Results")

    @api.onchange(
        "partner_id",
        "vat",
        "company_registry",
        "search_term",
        "zip",
        "city",
        "country_code",
    )
    def _onchange_search_terms(self):
        self.ensure_one()
        self.display_search_button = True

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        if "partner_id" in result:
            partner = self.env["res.partner"].browse(result["partner_id"])
            result.update(
                {
                    "search_term": partner.name,
                    "vat": partner.vat,
                    "company_registry": partner.company_registry,
                    "zip": partner.zip,
                    "city": partner.city,
                    "country_code": (code := partner.country_id.code)
                    in ALLOWED_COUNTRY_CODES
                    and code
                    or COUNTRY_CODE_BELGIUM,
                }
            )
        return result

    def open(self):
        self.ensure_one()
        action = self.get_formview_action()
        action.update(
            {
                "name": "Search Liza",
                "target": "new",
            }
        )
        return action

    def liza_search(self):
        """
        Get search results and create wizard lines.

        A VAT number or a Company ID is an exact identifier: Liza returns a
        single company for it, which we apply straight to the partner instead
        of asking the user to pick from a one-line result list. A free-text
        search term returns a list of candidates to choose from.
        """
        self.ensure_one()
        if not self.partner_id._liza_ensure_credentials():
            return self.partner_id._liza_call_wizard_credentials()
        args = {
            "vat": self.vat,
            "registry": self.company_registry,
            "search": self.search_term,
            "zip": self.zip,
            "city": self.city,
            "country_code": self.country_code,
        }
        error, results = self.partner_id._liza_call_get(args)
        if error:
            raise exceptions.ValidationError(error)
        # GetCompanyByVat / GetCompanyByRegistrationNumber return a single
        # company (a dict); SearchCompanies returns a list of candidates.
        if isinstance(results, dict):
            if not results:
                raise exceptions.ValidationError(
                    self.env._("Liza: no company found for the given identifier")
                )
            return self._liza_apply_single(results)
        line_vals = []
        for item in results:
            line_vals.append(
                {key: item.get(value) for key, value in SEARCH_RESULT_KEYS.items()}
            )
        self.line_ids = [Command.clear()] + [Command.create(val) for val in line_vals]
        self.display_search_button = False
        return self.open()

    def _liza_apply_single(self, response):
        """Apply an exact-match company response to the partner: store the
        identifier and country, fill the Liza fields from the response we
        already fetched, and copy the data onto the contact."""
        partner = self.partner_id
        values = {}
        if self.vat:
            values["vat"] = self.vat
        if self.company_registry:
            values["company_registry"] = self.company_registry
        if self.country_code:
            country = self.env["res.country"].search(
                [("code", "=", self.country_code)], limit=1
            )
            if country:
                values["country_id"] = country.id
        partner.write(values)
        partner.liza_error = False
        partner._liza_populate(response)
        partner.liza_button_copy_address()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": self.env._("Successfully fetched Liza data"),
                "sticky": False,
                "next": {
                    "type": "ir.actions.client",
                    "tag": "soft_reload",
                },
            },
        }
