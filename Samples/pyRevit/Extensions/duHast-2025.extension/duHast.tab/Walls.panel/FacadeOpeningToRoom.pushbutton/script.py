"""
An extension reporting external wall and window opening areas per room to a csv file.

Usage:

- Run the script.
- Select the rooms to report on.
- Select a location to save the csv file to.

Note:

- The external wall types, window opening families and phase of interest are configured in
  the rooms.rooms_facade_openings module.
"""

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc


# import facade openings reporting from library
from rooms.rooms_facade_openings import rooms_facade_openings_entry

# report facade opening per rooms
rooms_facade_openings_entry(doc=doc, output=output, forms=forms)
