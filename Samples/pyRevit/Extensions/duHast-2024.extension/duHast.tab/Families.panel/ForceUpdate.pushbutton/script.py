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

# create default catalogue type in family
from families.force_update import force_update_entry

force_update_entry(doc=doc, output=output, forms=forms)