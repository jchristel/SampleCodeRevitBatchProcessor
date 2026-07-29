print("Oh, hi there! This is the doors collector script running...")

import sys
import os

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()
# get the revit document
doc = revit.doc


# import doors exporter
from data.Collectors.doors import doors_export_entry

# run the exporter
doors_export_entry(doc, output, forms)
