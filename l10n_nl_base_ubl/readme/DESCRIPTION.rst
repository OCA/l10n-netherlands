This localization module provides functions that facilitate working with UBL
documents with the specific dialect that is used in Netherlands (NLCIUS).
For more info on the NLCIUS standard see:

https://www.forumstandaardisatie.nl/open-standaarden/nlcius

Partner identification
----------------------

According to NLCIUS, a Dutch commercial partner can be identified with:

- Kamer van Koophandel (KvK).
- Organisatie-identificatienummer (OIN).

In case OCA module `partner_coc` is installed, this module will handle the proper
value of KvK. Otherwise if the field KvK is defined in another module,
you should extend method ``_l10n_nl_base_ubl_get_kvk`` returning your custom KvK field.

In case OCA module `l10n_nl_oin` is installed, this module will handle the proper
value of OIN. Otherwise if the field OIN is defined in another module,
you should extend method ``_l10n_nl_base_ubl_get_oin`` returning your custom OIN field.
