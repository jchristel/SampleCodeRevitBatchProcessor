"""
An extension to propagate category visibility settings from one view template to many others in the same project file.

Usage:

- Run this script
- Select the categories of which the visibility settings are to be propagated.
- Select the view templates to apply the category settings to.
- press "Apply" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import levels and headers from library
from views.view_templates_overrides_categories import apply_graphic_overrides_to_views

# apply selected graphic overrides from one template to many
apply_graphic_overrides_to_views(doc, forms)
