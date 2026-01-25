print("Oh, hi there! This is poc of doc manager integration...")

import sys
import os

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()
# get the revit document
doc= revit.doc


# import ceiling exporter
from export.docManagerIntegration import ListDocuments
ListDocuments.main()