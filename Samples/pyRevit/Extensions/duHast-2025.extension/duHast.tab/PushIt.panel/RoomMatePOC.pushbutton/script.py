"""
An extension used to send revit room data to a local server.


"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# create default catalogue type in family
from pushIt_associated.room_mate.room_mate import rooms_export_entry

rooms_export_entry(doc=doc, uiapp=uiapp, output=output, forms=forms)