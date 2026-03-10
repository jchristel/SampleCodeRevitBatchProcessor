# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

from views.export_room_filter_from_schedules import export_room_filter_values_from_schedules_entry

print ("Exporting Room Number filter value...")

export_result = export_room_filter_values_from_schedules_entry(doc, output, forms)