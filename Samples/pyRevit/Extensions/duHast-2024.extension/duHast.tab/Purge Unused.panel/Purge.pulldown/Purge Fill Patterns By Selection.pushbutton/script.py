"""
An extension to purge selected fill patterns.

Note:

- This script implements a try and roll back pattern to identify any fill patterns nominated to be purged that are in use. If a fill pattern is in use, it will not be purged.
- Any fill patterns used in filled region definitions will not be offered in the selection window, As they are in use.
- This process is very time consuming and may take a while (hours) to complete depending on the size of the model.

Usage:

- Run this script
- Select the fill patterns to be purged.
- press "Purge" button.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# purge fill patterns by selection

from purge.purge_patterns_and_styles import purge_fill_patterns_by_selection

purge_fill_patterns_by_selection(doc=doc, output=output, forms=forms)
