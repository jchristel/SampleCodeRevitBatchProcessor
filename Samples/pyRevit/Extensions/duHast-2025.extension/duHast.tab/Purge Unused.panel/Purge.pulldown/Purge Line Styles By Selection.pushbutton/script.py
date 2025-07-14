"""
An extension to purge selected line styles.

Note:

- This script implements a try and roll back pattern to identify any line styles nominated to be purged that are in use. If a line style is in use, it will not be purged.

Usage:

- Run this script
- Select the line styles to be purged.
- press "Purge" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# purge line styles
from purge.purge_patterns_and_styles import purge_line_styles_by_selection

purge_line_styles_by_selection(doc=doc, output=output, forms=forms)
