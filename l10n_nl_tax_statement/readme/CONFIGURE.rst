This module makes use of the tax tags (eg.: 1a, 1b, 1c, 1d, 2a...) as prescribed by the Dutch tax laws.

If the default Odoo Dutch chart of accounts is installed (module ``l10n_nl``) then these tags are automatically present in the database.

If a non-standard chart of accounts is installed, you have to manually create the tax tags and properly set them into the tax definition.
The name of the tags must be formatted this way: "+1a (omzet)", "+1a (btw)", "-1a (omzet)", "-1a (btw)", "+2a (omzet)", "+2a (btw)", etc...

If your Company adopts the *Factuurstelsel* system for the accounting, also install the module ``l10n_nl_tax_invoice_basis``
(for more information about the installation and configuration of that module, check the README file).

The user must belong to the *Show Full Accounting Features* group, to be able to access the `Invoicing -> Configuration -> Accounting -> NL BTW Tags` menu.
