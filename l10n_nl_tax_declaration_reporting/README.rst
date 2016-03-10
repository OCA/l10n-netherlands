.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=========================
NL Tax Declaration Report
=========================

This module provides you with the Tax Statement in the Dutch format.
In the report you will find the taxes charged to customers and taxes that
suppliers charge to you. The layout this module provides will seem very
familiar to everyone wanting to declare taxes in The Netherlands.

The standard Tax Declaration report is not replaced by this module, a new
report with the Dutch layout is added to the menu
Reporting > Generic Reporting > Taxes.

Deze module biedt u de BTW aangifte in Nederlands formaat.
In het rapport staat de BTW berekend aan klanten, en de btw die
leveranciers aan u berekenen. Het rapport is met deze indeling zeer
herkenbaar voor iedereen die een belasting aangifte wilt doen.

Dit rapport verwijdert niet de standaard, maar wordt toegevoegd in
het menu Rapportages > Algemene rapporten > Belastingen.

Installation
============

This module can be installed using the standard installation procedure.

Configuration
=============

This module depends on the tax codes (e.g. 1a, 1b, 1c, 1d, 2a...) as prescribed
by the Dutch tax laws.

To use this module, the user should have installed the default Dutch chart of accounts
and not changed the tax code names. Alternatively be sure that a similar structure
for the the tax code names is recreated.

When using the default Dutch chart of account, the module l10n_nl will be installed,
which will add these codes automatically.

Usage
=====

The standard Tax Declaration report is not replaced by this module, a new
report with the Dutch layout is added to the menu
Reporting > Generic Reporting > Taxes.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/176/8.0

Known issues / Roadmap
======================

* Replace old with new API wizzard.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/l10n-netherlands/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/l10n-netherlands/issues>`_.


Credits
=======

Contributors
------------

* Diego Luis Neto <d.l.neto@onestein.nl>
* Kevin Graveman <k.graveman@onestein.nl>
* Richard Dijkstra <r.dijkstra@onestein.nl>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.