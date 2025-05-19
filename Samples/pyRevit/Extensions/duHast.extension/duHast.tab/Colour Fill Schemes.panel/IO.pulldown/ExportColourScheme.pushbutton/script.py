# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc


# import colour fill scheme exporter
from colour_schemes.colour_scheme_export import export_colour_scheme_entry

# export room filters from schedules
export_colour_scheme_entry(doc,  output, forms)