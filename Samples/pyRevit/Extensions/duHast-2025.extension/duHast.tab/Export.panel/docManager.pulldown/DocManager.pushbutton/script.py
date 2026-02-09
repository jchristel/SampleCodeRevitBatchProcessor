print("Oh, hi there! This is the doc manager running...")

import sys
import os

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()
# get the revit document
doc= revit.doc
uiapp = __revit__


# import ceiling exporter
from export.docManagerIntegration.doc_manager import doc_manager_entry

# run the exporter 
doc_manager_entry(doc=doc, uiapp = uiapp, output=output, forms=forms)
