print("hello world")

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc


# import grids and bubbles from library
from rooms.rooms_facade_openings import rooms_facade_openings_entry

# report facade opening per rooms
rooms_facade_openings_entry(doc=doc, output=output, forms=forms)