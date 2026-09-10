"""
An extension to export ceiling data to room mate.

Usage:

- Run this script with the model(s) holding the ceilings open or linked.

Two things about a ceilings run differ from the other buttons on this panel:

- A ceilings push carries no room reference at all, so it can never be pushed
  too early. Doors and windows name their rooms by id and FF&E names one; a
  Revit ceiling has no room parameter and a room has no ceiling parameter, so
  the server derives the association from polygon overlap on every read. Push
  ceilings before their rooms and nothing dangles -- they attribute to nothing
  until the rooms land, and then they do.
- A ceiling whose geometry could not be measured is still pushed, with an empty
  outline, so "no such ceiling" and "a ceiling nobody could measure" stay
  distinguishable. The export reports "N of M ceilings exist in phase X" for
  every model -- read that line, and note it FAILS the model if the export comes
  back short of the model's own count, which is what an older duHast does.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# import ceilings exporter
from room_m.room_mate import ceilings_export_entry

# exports ceiling data from the selected models
ceilings_export_entry(doc, uiapp, output, forms)
