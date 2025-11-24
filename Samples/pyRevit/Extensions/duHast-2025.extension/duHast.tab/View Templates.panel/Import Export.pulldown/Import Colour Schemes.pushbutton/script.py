# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# import scheme importer
from colour_schemes.colour_scheme_import import import_colour_scheme_entry

# import colour fill scheme 
import_colour_scheme_entry(doc,  output, forms)