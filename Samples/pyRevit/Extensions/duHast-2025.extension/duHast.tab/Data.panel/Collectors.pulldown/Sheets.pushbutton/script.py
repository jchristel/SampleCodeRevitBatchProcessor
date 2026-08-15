print("Oh, hi there! This is the sheets collector script running...")

import sys
import os

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()
# get the revit document
doc= revit.doc



# import sheet exporter
from data.Collectors.sheets import sheets_export_entry

# run the exporter 
sheets_export_entry(doc, output, forms)
