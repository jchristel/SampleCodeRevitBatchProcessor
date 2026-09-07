"""
An extension to export MEP space data to room mate.

Usage:

- Run this script with the services model(s) open or linked.

Two things about a spaces run differ from every other button on this panel:

- A run pushes ONE phase, and the disciplines do not always agree on what it is
  called. The export reports "N of M spaces are in phase X" for every model --
  read that line. Two runs, one per phase, is the answer when it looks wrong.
- A model holding no spaces is pushed as an empty result rather than refused.
  "This services model was audited and holds none" is a finding, and a different
  fact from the model never having been pushed.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# import spaces exporter
from room_m.room_mate import spaces_export_entry

# exports space data from the selected models
spaces_export_entry(doc, uiapp, output, forms)
