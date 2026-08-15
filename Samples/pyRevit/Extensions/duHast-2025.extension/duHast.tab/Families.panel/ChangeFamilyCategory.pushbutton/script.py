"""
An extension changing the category of the family open in the family editor.

Any subcategories are preserved: they are recreated under the new category and elements are
re-assigned to them.

Note:

- This runs on the open family document only, not on families loaded in a project.
- The family is not saved by this script.

Usage:

- Open the family in the family editor.
- Run the script.

    - Select the new category.
    - The progress will be displayed in the output window.

"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# change the category of a family
from families.category_change import change_category_entry
change_category_entry(doc=doc, output=output, forms=forms)