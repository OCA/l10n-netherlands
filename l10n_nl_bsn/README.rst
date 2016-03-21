.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================
Burgerservicenummer (BSN) for Partners
======================================

This module adds the BSN (Burgerservicenummer) field on partner forms.

The field is visible when the flag is_company is false.

A double check on the BSN is done when inserting/modifying its value:
 - validation of the BSN (check whether the format is correct);
 - check if another partner with the same BSN already exists.
In both cases, a non-blocking alert is shown.

**Warning**

It is forbidden to use the BSN if this is not required by a legal context.
Please check if you comply with all the legal and privacy aspects regarding the use of BSN in Odoo:

 - link1: https://autoriteitpersoonsgegevens.nl/nl/onderwerpen/identificatie/burgerservicenummer-bsn
 - link2: https://www.rijksoverheid.nl/onderwerpen/persoonsgegevens/inhoud/burgerservicenummer-bsn



Installation
============

The module depends on the external library 'python-stdnum'.

You can install that library by using pip:

* pip install python-stdnum


Configuration
=============

For security reasons the BSN number should be only visible to HR related roles.
Otherwise this will be in violation to the security framework of WBP regarding
the protection of persons info.

To be able to see the BSN number, give the proper permits to the user:

* User must belong to the "HR Officer" group


Usage
=====

To use this module, you need to:

* Open a form of a contact, eg.: a person (uncheck the flag "Is a Company?")
* Enter a BSN number

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/176/8.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/l10n-netherlands/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
l10n-netherlands/issues/new?body=module:%20
l10n_nl_bsn%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Andrea Stirpe <a.stirpe@onestein.nl>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
