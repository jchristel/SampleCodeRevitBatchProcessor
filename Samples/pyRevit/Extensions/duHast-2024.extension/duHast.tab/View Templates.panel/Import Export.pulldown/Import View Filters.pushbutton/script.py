"""
An extension to import category override settings from file.

Note:

- The imported filters will be applied to the current document.


Usage:

- Run this script
- Select the template export file.
- press "Import" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import levels and headers from library
from views.FiltersIO.filters_import import import_view_filters

# import view filters from file
import_view_filters(doc=doc, output=output, forms=forms, debug=False)
