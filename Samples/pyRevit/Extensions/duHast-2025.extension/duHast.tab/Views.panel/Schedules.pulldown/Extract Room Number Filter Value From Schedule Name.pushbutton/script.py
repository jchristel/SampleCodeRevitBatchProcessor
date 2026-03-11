# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

from views.Schedules.extract_schedule_name_to_room_filter import extract_room_filter_values_from_schedules_name_and_update_room_filter_entry

print ("Exporting Room Number filter value...")

export_result =extract_room_filter_values_from_schedules_name_and_update_room_filter_entry(doc, output, forms)