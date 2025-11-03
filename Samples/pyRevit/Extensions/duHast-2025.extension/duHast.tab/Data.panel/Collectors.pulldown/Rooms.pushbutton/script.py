print("Oh, hi there! This is the rooms collector script running...")

import sys
import os

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()
# get the revit document
doc= revit.doc


# import ceiling exporter
from data.Collectors.rooms import rooms_export_entry

# run the exporter 
rooms_export_entry(doc, output, forms)
