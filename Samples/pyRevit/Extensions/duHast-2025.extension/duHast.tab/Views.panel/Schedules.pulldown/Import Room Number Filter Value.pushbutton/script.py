# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

from views.import_room_filters_to_schedules import import_room_filter_values_to_schedules_entry
print ("Importing Room Number filter value...")


import_result = import_room_filter_values_to_schedules_entry(doc, output, forms)