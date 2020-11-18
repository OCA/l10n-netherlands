This module adds the Dutch `Organisatie-identificatienummer (OIN)` field
on partner forms.

The field is visible when the partner is a company.

A double check on the OIN is done when inserting/modifying its value:

- validation of the OIN (check whether the format is correct);
- check if another partner with the same OIN already exists.

In both cases, a non-blocking alert is shown.
