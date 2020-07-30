In the Netherlands, two types of accounting systems are allowed:

* Kasstelsel
* Factuurstelsel

By installing this module, you have the option to adopt the *Factuurstelsel* system for your Company in Odoo.
It means that, when validating an invoice, the system uses the invoice date instead of accounting date to determine the date of the move line for tax lines.
See https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_aangifte_doen_en_betalen/bereken_het_bedrag/hoe_berekent_u_het_btw_bedrag/factuurstelsel

Without this module installed for example, when you use an accounting date with vendor invoices, the *Generic TAX reports* and the *Aangifte omzetbelasting* show the VAT in the wrong period/date.
So this module is meant to fill the gap between the standard Odoo way and the *Factuurstelsel* system, commonly used in the Netherlands.

The *Kasstelsel* system instead is provided by the standard Odoo module ``account_tax_cash_basis``.
Find more information about the kasstelsel system in: https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_aangifte_doen_en_betalen/bereken_het_bedrag/hoe_berekent_u_het_btw_bedrag/kasstelsel/kasstelsel
