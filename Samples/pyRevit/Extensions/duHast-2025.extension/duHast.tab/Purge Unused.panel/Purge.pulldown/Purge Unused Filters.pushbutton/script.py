"""
An extension to purge unused view filters from the model.

Usage:

- Run this script
- select any view filters you would like to delete
- press "Purge" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# purge unused views filters
from purge.purge_views import purge_unused_view_filters

purge_unused_view_filters(doc=doc, output=output, forms=forms)
