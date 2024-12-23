"""
An extension to purge unused legends from the model.

Usage:

- Run this script
- select any unplaced legends you would like to delete
- press "Purge" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# purge unplaced legends
from purge.purge_views import purge_unused_legends

purge_unused_legends(doc=doc, output=output, forms=forms)
