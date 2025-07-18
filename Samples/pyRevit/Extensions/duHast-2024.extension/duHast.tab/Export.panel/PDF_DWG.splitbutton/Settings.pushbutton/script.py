"""
Creates and saves Export PDF and DWG settings in a project file.

"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# setup exporter settings
from export.export_pdf_dwg_settings import settings_export_pdf_dwg_entry

settings_export_pdf_dwg_entry(doc=doc, output=output, forms=forms)