# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc


print ("Importing schedule column widths from file...")

from views.Schedules.import_schedule_column_width import import_schedules_column_width_entry



import_result = import_schedules_column_width_entry(doc, output, forms)