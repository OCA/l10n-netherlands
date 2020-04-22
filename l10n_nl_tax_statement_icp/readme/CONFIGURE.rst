This module makes use of the tax tags "3b" and "3b diensten".

If the default Odoo Dutch chart of accounts is installed (module ``l10n_nl``) then "3b" tag is automatically present in the database.
In this case you should add the "3b diensten" teg and set it into the tax definition.

If a non-standard chart of accounts is installed, you have to manually create the tax tags and properly set them into the tax definition.
The name of the tags must be formatted this way: "+3b (omzet)", "-3b (omzet)", "+3b diensten (omzet)", "-3b diensten (omzet)".
