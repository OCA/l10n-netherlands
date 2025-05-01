This module will make the KvK number of a partner available as the field that
was used in Odoo 16.0 and earlier. After Odoo 16.0, the field is replaced by
the generic mechanism using two fields: Peppol Endpoint and Peppol EAS.

This module will use these fields in the backend to display and store the KvK
number when viewed or altered on the partner form. This can help when backwards
compatibility is required, but having the single field available also provides
better usablility than having to enter the Peppol Endpoint and Peppol EAS
separately (at least for instances or companies in instances that focus mainly
on partners with a KvK number).
