"""
An extension to purge unused shared parameters from the model.

Note:

- This script implements a try and roll back pattern to identify any shared parameters to be purged that are in use. If a shared parameter is in use, it will not be purged.
- Any shared parameters with category bindings will be removed from the overall set to be purged, as they are in use.
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

# purge shared parameters
from purge.purge_shared_parameters import purge_shared_parameters

purge_shared_parameters(doc=doc, output=output, forms=forms)