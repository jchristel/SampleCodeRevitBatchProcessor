"""
An extension to purge unplaced views from the model.

Note:

- This script will not offer up any view to be purged, if a dependent of the view is placed on a sheet.

Usage:

- Run this script
- select any unplaced views you would like to delete
- press "Purge" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# purge unplaced views
from purge.purge_views import purge_unplaced_views

purge_unplaced_views(doc=doc, output=output, forms=forms)
