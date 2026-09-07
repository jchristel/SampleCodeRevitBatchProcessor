"""
An extension to export ffe data to room mate.

Usage:

- Run this script in a view where you want to export ffe data to room mate.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# import ffe exporter
from room_m.room_mate import ffe_export_entry

# exports ffe data from the selected models
ffe_export_entry(doc, uiapp, output, forms)

