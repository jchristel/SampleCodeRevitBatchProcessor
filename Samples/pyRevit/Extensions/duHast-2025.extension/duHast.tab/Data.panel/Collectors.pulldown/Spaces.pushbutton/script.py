print("Oh, hi there! This is the spaces collector script running...")

import sys
import os

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()
# get the revit document
doc= revit.doc


# import space exporter
from data.Collectors.spaces import spaces_export_entry

# run the exporter 
spaces_export_entry(doc, output, forms)
