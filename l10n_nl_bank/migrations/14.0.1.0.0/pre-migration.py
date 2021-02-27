# 2021 Bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

"""
Change typo in XML_ID of Knab
"""


def migrate(cr, version):

    cr.execute(
        """UPDATE ir_model_data
        SET
            name = 'KNAB'
        WHERE
            name = 'KNAP' and module='l10n_nl_bank';
        """
    )
