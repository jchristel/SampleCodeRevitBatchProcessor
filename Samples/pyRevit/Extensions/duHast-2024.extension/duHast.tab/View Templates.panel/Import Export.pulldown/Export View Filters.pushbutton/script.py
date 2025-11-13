"""
An extension to export view filters to file.

Note:

- The exported settings can be imported back into other files and will only view filters with the same name.


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

# import view filters from library
from views.FiltersIO.filter_export import export_view_filters

# export view filters
export_view_filters(doc=doc, output=output, forms=forms, debug=False)
