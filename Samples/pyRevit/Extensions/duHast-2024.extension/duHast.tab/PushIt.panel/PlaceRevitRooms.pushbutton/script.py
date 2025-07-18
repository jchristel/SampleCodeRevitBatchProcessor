"""
An extension used to place revit rooms in the current Revit model based on pushIt rooms.


"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# create default catalogue type in family
from pushIt_associated.place_revit_rooms.place_revit_rooms import place_revit_rooms_entry

place_revit_rooms_entry(doc=doc, uiapp = uiapp, output=output, forms=forms)