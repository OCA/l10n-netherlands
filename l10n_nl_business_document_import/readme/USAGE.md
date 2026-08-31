The partner matching is extended with two extra lookups, tried in this
order before the standard matching on contact, name, website and e-mail:

1.  `company_registry` on the partner, which holds the Dutch chamber of
    commerce number (KvK). This field is provided by Odoo itself.
2.  `l10n_nl_oin` on the partner, the Dutch
    Organisatie-identificatienummer.

Both are read from the `partner_dict` passed to `_match_partner()`,
under the keys `company_registry` and `l10n_nl_oin`.

The OIN lookup is an *optional* feature: the module *l10n_nl_oin* is not
a dependency. When it is not installed, the `l10n_nl_oin` key is simply
ignored and only the chamber of commerce number is used. Install
*l10n_nl_oin* to enable matching on the OIN as well.
