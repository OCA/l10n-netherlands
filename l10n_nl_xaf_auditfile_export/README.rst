.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
XAF auditfile export
====================

This module allows you to export XAF audit files for the Dutch tax authorities (Belastingdienst).

The currently exported version is 3.2

Configuration
=============

This module works on huge amount of data, so there is a possibility to encounter out of memory exceptions. In this case. set the config parameter `l10n_nl_xaf_auditfile_export.max_records` to a value much lower than 10000.

Usage
=====

To use this module, you need to:

* go to `Invoicing`/`Reporting`/`Legal Reports`/`Auditfile export`
* create a new record, adjust values if the defaults are not appropriate
* click `Generate auditfile`
* click `Download` on the field `Auditfile`

For further information, please visit:

* https://www.odoo.com/forum/help-1

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/176/10.0

Known issues / Roadmap
======================

* encrypted and compressed files would be nice


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/l10n-netherlands/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>
* Andrea Stirpe <a.stirpe@onestein.nl>

Icon
----

https://openclipart.org/detail/180891

Documentation
-------------

http://www.softwarepakket.nl/swpakketten/auditfiles/auditfile_financieel.php?bronw=6

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
