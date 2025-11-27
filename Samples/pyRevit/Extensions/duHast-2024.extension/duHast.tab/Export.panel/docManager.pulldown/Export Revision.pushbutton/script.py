print("Oh, hi there! This is the revision exporter script running...")

import sys
import os

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()
# get the revit document
doc= revit.doc


# import ceiling exporter
from export.docManagerIntegration.ExportRevs.export_revisions import export_revs_entry

# run the exporter 
export_revs_entry(doc, output, forms)
