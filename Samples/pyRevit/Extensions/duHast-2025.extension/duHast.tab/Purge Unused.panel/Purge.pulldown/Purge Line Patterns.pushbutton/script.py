"""
An extension to purge line patterns from the model.

Note:

- This script implements a try and roll back pattern to identify any line patterns to be purged that are in use. If a line pattern is in use, it will not be purged.

Usage:

- Run this script
- press "Purge" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# purge line patterns
from purge.purge_patterns_and_styles import purge_line_patterns

purge_line_patterns(doc=doc, output=output, forms=forms)
