"""
Compares sheets in a schedule to files in a folder.

"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# compare sheets in schedule to files in folder
from export.CompareRevitToFolder.compare_revit_schedule_to_folder import compare_entry

compare_entry(doc=doc, output=output, forms=forms)