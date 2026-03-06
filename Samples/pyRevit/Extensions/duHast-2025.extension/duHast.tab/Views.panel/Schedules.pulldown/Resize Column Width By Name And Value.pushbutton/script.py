# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc


print ("Resizes a specific column in selected schedules by a given value")

from views.Schedules.adjust_specific_schedule_field_width import import_schedules_column_width_entry



import_result = import_schedules_column_width_entry(doc, output, forms)