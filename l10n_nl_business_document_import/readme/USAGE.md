The partner matching is extended with three extra lookups, tried in this
order before the standard matching on contact, name, website and e-mail:

1. `company_registry` on the partner, the generic company identifier
   provided by Odoo itself.
2. The Peppol endpoint with EAS `0106`, which is the Dutch chamber of
   commerce number (KvK).
3. The Peppol endpoint with EAS `0190`, which is the
   Organisatie-identificatienummer (OIN).

These are read from the `partner_dict` passed to `_match_partner()`, under
the keys `company_registry`, `l10n_nl_kvk` and `l10n_nl_oin` respectively.

As of Odoo 17 the KvK number and the OIN are no longer stored in a dedicated
field. They are held in the generic `peppol_endpoint` field of the partner,
and the `peppol_eas` field states which of the two the number is. Matching
therefore always takes the EAS code into account: a KvK number will not match
a partner that has the same digits registered as an OIN.

The module *l10n_nl_kvk_partner* can be used to display and edit the KvK
number as a single field on the partner form.
