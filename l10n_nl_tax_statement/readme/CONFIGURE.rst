This module makes use of the tax tags (eg.: 1a, 1b, 1c, 1d, 2a...) as prescribed by the Dutch tax laws.

If the default Odoo Dutch chart of accounts is installed (module ``l10n_nl``) then these tags are automatically present in the database.

If a non-standard chart of accounts is installed, you have to manually create the tax tags and properly set them into the tax definition.
The name of the tags must be formatted this way: "+1a (omzet)", "+1a (btw)", "-1a (omzet)", "-1a (btw)", "+2a (omzet)", "+2a (btw)", etc...

This module provides an accounting setting *Invoice basis* (Factuurstelsel)
that is enabled by default. This option makes the *invoice date* leading for
the tax declaration of a period, rather than the accounting date, and
allows you to change the accounting date of incoming invoices to the period
to which the costs apply and still create a legally valid Dutch tax
declaration. Without this option, the entries on the tax statement are
collected using only their accounting dates (what Odoo calls *standard
taxes*).

This setting is not compatible with the Odoo *Cash basis* (Kasstelsel) setting
which leads to the creation of tax journal lines at the moment that a payment
is received, so when using *Cash basis* you need to disable the *Invoice
basis* setting to create a valid Dutch tax declaration using this module.
To disable the *Invoice basis* for a company, you need to:

#. Open your Company form and verify that Country is set to ``Netherlands``.
#. Go to ``Invoicing -> Configuration -> Settings``, enable/disable ``NL Tax Invoice Basis (Factuurstelsel)`` and ``Apply``.
