For developers
--------------

Most of what this addon does is copying the original vat statement model to a new model ``l10n.nl.icp.statement``, and adapting one2many fields such that they point to this new model. In order to do so, new many2one fields have to be added to all the referenced models, like account.move or account.move.line. The rest is using various techniques to make the code of the original model work on the newly added fields instead of the original ones.

So when migrating this module, watch out for one2many fields being added to the ``l10n.nl.vat.statement`` model, they most likely will need to be adapted in the ICP model. Also check that the overrides meant to change actions on ``l10n_nl_vat_statement_id`` to ``l10n_nl_icp_statement_id`` are still functional and needed.
