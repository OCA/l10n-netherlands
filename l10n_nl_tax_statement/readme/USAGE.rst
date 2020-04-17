To create a statement you need to:

#. Verify that you have enough permits. You need to belong to the *Show Full Accounting Features* group.
#. Go to the menu: `Invoicing -> Reporting > NL BTW Statement`
#. Create a statement, providing a name and specifying start date and end date
#. Press the Update button to calculate the report: the report lines will be displayed in the tab `Statement`
#. Manually enter the BTW amounts of lines '5d', '5e', '5f' (in Edit mode, click on the amount of the line to be able to change it)
#. Press the Post button to set the status of the statement to Posted; the statements set to this state cannot be modified

To add past undeclared invoices/moves:

#. Open the tab `Past Undeclared Moves`, available when the statement is in status Draft.
#. Set an initial date (field From Date) from which the past undeclared moves will be displayed.
#. One by one, add the displayed undeclared moves, by clicking on the `Add Move` button present in each line.
#. Press the Update button in order to recompute the statement lines.

Extra info about the workflow:

#. If you need to recalculate or modify or delete a statement already set to Posted status you need first to set it back to Draft status: press the button Reset to Draft
#. Instead, if you send the statement to the Tax Authority, you may want to avoid that the statement is set back to Draft: to avoid this, press the button Final. If you then confirm, it will be not possible to modify this Statement or reset it back to draft anymore.

Printing a PDF report:

#. If you need to print the report in PDF, open a statement form and click: `Print -> NL Tax Statement`

Multicompany fiscal unit:

#. According the Dutch Tax Authority, for all the companies belonging to a
   fiscal unit, it's possible to declare one single tax statement.
#. To create one tax statement for a fiscal unit, log in into the parent
   company and select the child companies in the statement (be sure the user
   belongs to the multicompany group).
#. The child companies must have the same Tax codes labels (Tax Tags) as the
   parent company, the same currency as the parent company and must be located
   in The Netherlands.
