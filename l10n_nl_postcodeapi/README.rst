Auto-completion for Dutch addresses
===================================
This module contains integration of the excellent and free address completion
service 'PostcodeAPI'. The service allows lookups by zip code and house number,
providing street name and city. The lookups will be triggered in the partner
form views when a zip code or house number is entered or modified. Only
Dutch addresses (which is assumed to include addresses with no country) are
auto-completed.

More info about the lookup service here: http://www.postcodeapi.nu/

Dependencies
============
This module depends on the module partner_street_number, which will split
up the street field into separate fields for street name and number.

You also need to have the 'pyPostcode' Python library by Stefan Jansen
installed (https://github.com/steffex/pyPostcode). Install in the following way
for now, until this lib is available on Pypi::

    pip install git+https://github.com/stefanrijnhart/pyPostcode.git@pypi

Configuration
=============
Please enter the API key that you request from PostcodeAPI into the system
parameter 'l10n_nl_postcodeapi.apikey'

Provinces are autocompleted if a country state with the exact name is found in
the system. A CSV file with the Dutch provinces is included in the data
directory, but not loaded by default. You can import the file manually.

Compatibility
=============
This module is compatible with OpenERP 8.0.

Credits
=======

Contributors
------------

* Stefan Rijnhart (Therp BV) <stefan@therp.nl>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA at https://github.com/OCA/l10n-netherlands

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
