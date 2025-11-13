"""
An extension to export category override settings from selected view templates to file.

Note:

- The exported settings can be imported back into other files and will only modify view templates with the same name.
- Override settings can be imported using the "Import View Templates" script.

Usage:

- Run this script
- select any view templates you want to export overrides from.
- press "Export" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import levels and headers from library
from views.view_templates_overrides_io import export_overrides_of_selected_viewtemplates

# apply selected graphic overrides from one template to many
export_overrides_of_selected_viewtemplates(doc=doc, output=output, forms=forms)