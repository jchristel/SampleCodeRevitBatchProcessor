# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc


# import grids and bubbles from library
from rooms.rooms_and_walls import walls_to_rooms_entry

# switches all bubbles in the active view off
walls_to_rooms_entry(doc=doc, output=output, forms=forms)