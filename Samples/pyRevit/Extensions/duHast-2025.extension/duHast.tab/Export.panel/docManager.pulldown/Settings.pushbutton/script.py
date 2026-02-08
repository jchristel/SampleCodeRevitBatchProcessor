"""
An extension used to save settings for docManager integration in a model using extended storage.

Usage:

- Run the script.


"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# save settings to model file using extended storage
from export.docManagerIntegration.doc_manager_settings import doc_manager_settings_entry

doc_manager_settings_entry(doc=doc, uiapp = uiapp, output=output, forms=forms)
