"""
An extension used to verify push it rooms areas by placing Revit rooms as a reference to the push it rooms.


"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# create default catalogue type in family
from pushIt_associated.area_by_room_verification.area_by_room_verification import push_it_area_by_room_verification_entry

push_it_area_by_room_verification_entry(doc=doc, uiapp = uiapp, output=output, forms=forms)