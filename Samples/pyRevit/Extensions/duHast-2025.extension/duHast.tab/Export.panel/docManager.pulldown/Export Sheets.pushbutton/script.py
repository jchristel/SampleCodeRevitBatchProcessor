print("Oh, hi there! This is the sheet exporter script running...")

import sys
import os

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()
# get the revit document
doc= revit.doc


# import ceiling exporter
from export.docManagerIntegration.ExportDocuments.export_sheets import export_sheets_entry

# run the exporter 
export_sheets_entry(doc, output, forms)
