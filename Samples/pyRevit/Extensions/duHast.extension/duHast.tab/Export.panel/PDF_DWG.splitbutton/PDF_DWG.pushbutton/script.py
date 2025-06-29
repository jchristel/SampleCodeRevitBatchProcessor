"""
Exports sheets to pdf and dwg files.

"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# export sheets to pdf and dwg files
from export.export_pdf_dwg_v2 import export_pdf_dwg_entry

export_pdf_dwg_entry(doc=doc, output=output, forms=forms)