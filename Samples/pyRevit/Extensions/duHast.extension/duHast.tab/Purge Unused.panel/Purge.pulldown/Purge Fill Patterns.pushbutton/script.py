"""
An extension to purge fill patterns in the model.

Note:

- This script implements a try and roll back pattern to identify whether a fill patterns is in use. If a fill pattern is in use, it will not be purged.
- Any fill patterns used in filled region definitions will be removed from the overall set to be purged, as they are in use.
- This process is very time consuming and may take a while (hours) to complete depending on the size of the model.

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

# purge unused fill patterns

from purge.purge_patterns_and_styles import purge_fill_patterns

purge_fill_patterns(doc=doc, output=output, forms=forms)
