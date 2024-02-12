This module integrates Odoo with the official Dutch chamber of commerce
`Kamer van Koophandel (KvK) API search <https://www.kvk.nl>`_.

The KvK API service allows lookups by the *Chamber Of Commerce Registration Number*
(KvK field) providing company name, street name, postcode and city. The lookups will be
triggered in the partner form views by entering a KvK field and pressing its lookup button.
The lookup works also on the company name field, providing Kvk number, street name, postcode
and city.

The KvK field is already provided by the OCA module `partner_coc`. That field is visible when
the partner is a Company (flag *is_company* = true).

More info about the lookup service here: https://developers.kvk.nl/documentation
