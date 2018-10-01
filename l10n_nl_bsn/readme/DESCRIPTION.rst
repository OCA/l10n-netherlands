This module adds the BSN (Burgerservicenummer) field on partner forms.

The field is visible when the field ``company_type`` is set to ``Individual``.

A double check on the BSN is done when inserting/modifying its value:

- validation of the BSN (check whether the format is correct);
- check if another partner with the same BSN already exists.

In both cases, a non-blocking alert is shown.
