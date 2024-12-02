The module relies on a list of known infixes to get the parsing right:

van, der, den, op, ter, de, v/d, d', 't, te

Also any combination, so *op den*, *van der* etc will also be recognized.

If you need a different set of infixes, set system parameter `l10n_nl_partner_name_infixes` to a comma separated list like

infix1,infix2,etc

Note this replaces the above list.
