# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# export sheets to pdf and dwg files
from export.docManager.database_setup import settings_database_entry

settings_database_entry(doc=doc, output=output, forms=forms)