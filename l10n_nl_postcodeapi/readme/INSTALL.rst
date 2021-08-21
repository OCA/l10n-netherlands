This module depends on the standard Odoo module base_address_extended, which will split
up the street field into separate fields for street name and number.

It now also depends on l10n_nl_country_states, to provide the names of the provinces,
that will be added to the res_country_state model.

You also need to have the 'pyPostcode' Python library by Stefan Jansen
installed (https://pypi.python.org/pypi/pyPostcode).
