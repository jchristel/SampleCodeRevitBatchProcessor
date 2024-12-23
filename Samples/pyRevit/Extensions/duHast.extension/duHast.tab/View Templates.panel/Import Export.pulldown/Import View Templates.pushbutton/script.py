"""
An extension to import category override settings from file.

Note:

- The imported overrides will only be applied to view templates with the same name as the ones in the file.
- Override settings are exported using the "Export View Templates" script.
- Custom sub-categories which do not exists in the target file will be ignored.

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
from views.view_templates_overrides_io import import_overrides_from_file

# import view templates overrides from file and apply to matching templates
import_overrides_from_file(doc=doc, output=output, forms=forms)
