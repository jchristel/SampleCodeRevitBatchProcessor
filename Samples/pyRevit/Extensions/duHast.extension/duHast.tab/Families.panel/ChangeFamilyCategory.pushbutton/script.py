"""
An extension applying a hack to force an update to a family when loaded into a project file

The hack is:
- create a new family type
- save the family
- delete the new family type
- save the family again


Usage:

- Run the script.

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