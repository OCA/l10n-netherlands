With this localization module, Odoo will be able to generate UBL XML documents
by identifying the Dutch commercial partner with:

- Kamer van Koophandel (KvK).
- Organisatie-identificatienummer (OIN).

In case OCA module `partner_coc` is installed, this module will handle the proper
value of KvK. Otherwise if the field KvK is defined in another module,
you should extend method ``_l10n_nl_ubl_get_kvk`` returning your custom KvK field.

In case OCA module `l10n_nl_oin` is installed, this module will handle the proper
value of OIN. Otherwise if the field OIN is defined in another module,
you should extend method ``_l10n_nl_ubl_get_oin`` returning your custom OIN field.
