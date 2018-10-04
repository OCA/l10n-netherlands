This module makes use of the tax tags (eg.: 1a, 1b, 1c, 1d, 2a...) as prescribed by the Dutch tax laws.

If the default Odoo Dutch chart of accounts is installed (module ``l10n_nl``) then these tags are automatically present in the database.
If this is the case, go to menu: `Invoicing -> Configuration -> Accounting -> NL BTW Tags`, and check that the tags are correctly set; click Apply to confirm.

If a non-standard chart of accounts is installed, you have to manually create the tax tags and properly set them into the tax definition.
After that, go to go to menu: `Invoicing -> Configuration -> Accounting -> NL BTW Tags`, and manually set the tags in the configuration form; click Apply to confirm.

If your Company adopts the *Factuurstelsel* system for the accounting, also install the module ``l10n_nl_tax_invoice_basis``
(for more information about the installation and configuration of that module, check the README file).

The user must belong to the *Show Full Accounting Features* group, to be able to access the `Invoicing -> Configuration -> Accounting -> NL BTW Tags` menu.
