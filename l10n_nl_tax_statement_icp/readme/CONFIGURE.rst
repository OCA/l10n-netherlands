To configure this module, you need to:

#. Follow the configuration steps as described in *l10n_nl_tax_statement* and set the tag *3b omzet* needed for this report.

On the ICP Statement, the amounts will be split up into an amount for products
and an amount for services. The Dutch chart of accounts in Odoo provides
a separate set of taxes for services which ensure that the amounts are split
up properly here as well. If you are migrating from a legacy situation or you
do not want to apply separate taxes to service products, you can set a *System
Parameter* with key
*l10n_nl_tax_statement_icp.icp_amount_by_tag_or_product* to value *product*.

With this configuration in place, the amounts will be split up according to
the product type, using service by default when no product is mentioned on
the invoice line.
