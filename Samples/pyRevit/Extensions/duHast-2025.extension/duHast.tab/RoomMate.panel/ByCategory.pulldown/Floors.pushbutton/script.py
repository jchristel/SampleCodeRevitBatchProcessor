"""
An extension to export floor data to room mate.

Usage:

- Run this script with the model(s) holding the floors open or linked.

Three things about a floors run differ from the other buttons on this panel:

- A floors push carries no room reference at all, so it can never be pushed
  too early. A Revit floor has no room parameter, so the server derives the
  association from polygon overlap on every read, exactly as it does for
  ceilings. Push floors before their rooms and nothing dangles.
- Every element in the Floors category is pushed: structural slabs, finish
  floors, build-ups, insulation, paving, lawns and roof layers modelled with the
  floor tool. Nothing filters them; the Structural parameter and the height
  offset travel with each one, and a floor belongs to the storey of the level
  it is hosted on.
- A room is only matched to floors in its OWN model. A project that keeps its
  slabs in a base-build model and its rooms in fit-out models will see those
  slabs attributed to no room.

Like ceilings, a floor whose geometry could not be measured is still pushed with
an empty outline, and the export reports "N of M floors exist in phase X" for
every model -- read that line. It FAILS the model if the export comes back short
of the model's own count, which is what an older duHast does.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# import floors exporter
from room_m.room_mate import floors_export_entry

# exports floor data from the selected models
floors_export_entry(doc, uiapp, output, forms)
