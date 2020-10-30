New fields are added to the title model to express the salutation of partners,
in combination with the gender field. Based on partner_name_dutch, you can
then refer to function fields generating full salutations to use at the
start of a letter, or short versions to be used in addresses.

The interface allows to change generated salutations manually, after which
these will not be updated anymore after changes in the partner name or title.
While the manually entered salutations are stored in separate fields, the
function fields refer to their values when manual changes are active so you
should always use the function fields in your document templates.

While organizations have no gender (the field is hidden there), you can have
a feminine salutation by creating a partner title with an implicit gender,
such as 'Ladies club'.
