print("Oh, hi there! This is the item collector script running...")

import sys
import os

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()
# get the revit document
doc = revit.doc


# import item exporter
from data.Collectors.items import items_export_entry

# run the exporter
items_export_entry(doc, output, forms)
