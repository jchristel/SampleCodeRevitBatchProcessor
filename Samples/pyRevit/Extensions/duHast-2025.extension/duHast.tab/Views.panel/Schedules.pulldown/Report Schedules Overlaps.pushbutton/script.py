# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc


print ("Fixing overlaps...")

from views.Schedules.report_schedule_segments_overlaps import report_schedule_segments_overlap_entry


result = report_schedule_segments_overlap_entry(doc, output, forms)