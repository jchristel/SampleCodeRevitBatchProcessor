"""
An extension to propagate view filter settings from one view template to many others.

Note:

- If the selected view filters does not exist in the target view templates, it will be ignored.

Usage:

- Run this script
- Select the view filters to be propagated.
- Select the view templates to apply the filters to.
- press "Apply" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import levels and headers from library
from views.view_templates_overrides_filters import apply_filter_overrides_to_views


# propagate filter overrides from one template to many
apply_filter_overrides_to_views(doc=doc, add_filter_if_not_present=False, forms=forms)
