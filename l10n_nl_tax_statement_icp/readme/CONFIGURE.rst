This module makes use of the tax tags "3b".

If the default Odoo Dutch chart of accounts is installed (module ``l10n_nl``) then "3b" tag is automatically present in the database.

If a non-standard chart of accounts is installed, you have to manually create the tax tags and properly set them into the tax definition.
The name of the tags must contain the substring "3b", eg.: be formatted this way: "3bl (omzet)", "3bt (omzet)".

Taxes should be set differently, whether they refer to products or services. In particular
the taxes for services should contain the "dienst" substring in the name. For example:
`Verkopen export binnen EU (producten)` for  products and `Verkopen export binnen EU (diensten)` for services.

Notice that, when selecting a product in invoice lines, its product type should be consistent with
the selected tax:

- a product of type "service" should have a tax with "dienst" in its name
- a consumable or storable product should have a tax without "dienst" in its name
