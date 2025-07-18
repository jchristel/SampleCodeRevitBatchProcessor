"""
An extension to purge any unused view templates the model.

Usage:

- Run this script
- select any unused view templates you would like to delete
- press "Purge" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# purge unused templates
from purge.purge_views import purge_unused_view_templates

purge_unused_view_templates(doc=doc, output=output, forms=forms)
