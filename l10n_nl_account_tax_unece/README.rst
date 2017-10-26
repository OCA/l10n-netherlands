.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=========================
L10n NL Account Tax UNECE
=========================

This module will auto-configure the values *UNECE Tax Type* and *UNECE Tax Category* on taxes that come from the *l10n_nl* module.

Both the values will also be set in the template of the tax accounts.
This will be useful in case of setting new companies with the Dutch chart of accounts in a multi-company environment.

Installation
============

This module will be installed automatically if modules ``l10n_nl`` and ``account_tax_unece`` are installed.

Usage
=====

#. Simply install the module to set the values *UNECE Tax Type* and *UNECE Tax Category* on existing taxes that come from the *l10n_nl* module.
#. If you create a new Dutch company and set its chart of accounts ( with the one that comes from *l10n_nl*), the newly created taxes will also get the values *UNECE Tax Type* and *UNECE Tax Category* set.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/176/10.0

Known issues / Roadmap
======================

* The definition of the fields *UNECE Tax Type* and *UNECE Tax Category* should be moved to module ``account_payment_unece``.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/l10n-netherlands/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

* This module, expecially the `post_install` script, is based on the job made by
    * Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
      Module: OCA/l10n-france/l10n_fr_account_tax_unece
      Link: https://github.com/OCA/l10n-france/tree/10.0/l10n_fr_account_tax_unece

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
