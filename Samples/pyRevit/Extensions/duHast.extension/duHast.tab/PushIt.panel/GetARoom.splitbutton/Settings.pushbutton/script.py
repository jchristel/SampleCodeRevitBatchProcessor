"""
An extension used to save settings for Get A Room in a model using extended storage.

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

# save settings to model file using extended storage
from pushIt_associated.get_a_room.settings_entry import get_a_room_settings_entry

get_a_room_settings_entry(doc=doc, uiapp = uiapp, output=output, forms=forms)
