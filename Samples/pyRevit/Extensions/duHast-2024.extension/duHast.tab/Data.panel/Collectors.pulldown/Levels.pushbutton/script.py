print("Oh, hi there! This is the level collector script running...")


import sys
import os

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()
# get the revit document
doc= revit.doc


# import ceiling exporter
from data.Collectors.levels import levels_export_entry

# run the exporter 
levels_export_entry(doc, output, forms)
