.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=========================
Netherlands ICP Statement
=========================

This module extends the *Netherlands BTW Statement* module (BTW aangifte report), by adding the statement for the *Intra-Community transactions declaration* (ICP declaration).

The ICP declaration report is based on line *3b - Leveringen naar landen binnen de EU (omzet)* of the BTW aangifte report.
The period is also the same as the one selected in the BTW aangifte report.

This ICP declaration report includes:

* the VAT identification numbers of your customers;
* the total amount of intra-Community supplies from the Netherlands for every customer during the selected period.

Installation
============

To install this module, you need to:

#. Install module *l10n_nl_tax_statement* version >= *11.0.2.0.0*.

Configuration
=============

To configure this module, you need to:

#. Follow the configuration steps as described in *l10n_nl_tax_statement* and set the tag *3b omzet* needed for this report.

Usage
=====

To use this module, you need to:

#. Create a BTW Statement.
#. Post the BTW Statement: a new tab *ICP Statement* will be displayed; the tab contains the lines of the ICP declaration report.
#. In tab *ICP Statement* press the Update button in order to recompute the ICP statement lines.

Printing a PDF report:

#. If you need to print the report in PDF, open a statement form and click: `Print -> NL ICP Statement`


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/176/11.0


Known issues / Roadmap
======================

* Add checks to avoid errors in the report, e.g. no country, wrong country, no VAT code, tax-code not matching fiscal position, etc..
* Add unit tests

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

* Andrea Stirpe <a.stirpe@onestein.nl>

Do not contact contributors directly about support or help with technical issues.

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
