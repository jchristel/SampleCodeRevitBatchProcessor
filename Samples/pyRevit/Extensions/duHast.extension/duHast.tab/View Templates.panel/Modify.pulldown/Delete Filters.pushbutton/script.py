"""
An extension to delete view filters from view templates.

Usage:

- Run this script
- Select the view filters to be deleted from the templates.
- Select the view templates to remove the filters from.
- press "Apply" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import levels and headers from library
from views.view_templates_overrides_filters import remove_filters_from_view_templates

# apply selected graphic overrides from one template to many
remove_filters_from_view_templates(doc=doc, output=output, forms=forms)
