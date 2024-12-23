"""
An extension to purge any schedules not placed on a sheet from the model.

Usage:

- Run this script
- select any unplaced schedules you would like to delete
- press "Purge" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# purge unplaced schedules
from purge.purge_views import purge_unused_schedules

purge_unused_schedules(doc=doc, output=output, forms=forms)
