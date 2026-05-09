print("Oh, hi there! This is the floor collector script running...")

import sys
import os

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()
# get the revit document
doc = revit.doc


# import floor exporter
from data.Collectors.floors import floors_export_entry

# run the exporter
floors_export_entry(doc, output, forms)
