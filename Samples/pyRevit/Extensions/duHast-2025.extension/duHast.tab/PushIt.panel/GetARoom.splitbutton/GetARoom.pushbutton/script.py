"""
An extension used to convert a filled region to a push it room

Usage:

- Run the script.


"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

#  convert filled regions to push iut rooms
from pushIt_associated.get_a_room.get_a_room import get_a_room_entry

get_a_room_entry(doc=doc, uiapp = uiapp, output=output, forms=forms)
