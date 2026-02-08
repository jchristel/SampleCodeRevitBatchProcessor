"""
An extension used to search, load and edit family in a central library.
"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# create default catalogue type in family
from families.at_the_library import at_the_library_entry

at_the_library_entry(doc=doc, uiapp=uiapp, output=output, forms=forms)