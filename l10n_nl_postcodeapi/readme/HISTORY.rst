11.0.2.0.0 (2021-08-21)
~~~~~~~~~~~~~~~~~~~~~~~

- Now depend on l10n_nl_country_states to prevent conflicts with that module;
- No manual caching of province data. It complicates code and performance gain
  will almost certainly be negligible;
- Check valid Api Key in configuration immediately when setting or updating key;
- Take into account that with l10n_nl_country_states installed, state_id on partner
  will in many cases be set, even if postcode api not active, or cannot find
  address;
- Adjust tests to run properly on databases already containing data.
