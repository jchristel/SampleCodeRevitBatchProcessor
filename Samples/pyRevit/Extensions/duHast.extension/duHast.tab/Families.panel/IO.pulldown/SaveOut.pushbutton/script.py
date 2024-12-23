"""
An extension to bulk save families from a project file into a directory.

This extension uses Revit's failure handling mechanism to suppress warnings and errors during the save process.

Usage:

- Run the script.
- Select all families in the project to be saved out.
- Select the directory.
- Click "Save".
- The script will save the families into the directory. Any existing files will be overwritten.

"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# save all families out - simple
from families.save_out import save_loaded_families_entry

save_loaded_families_entry(doc=doc, output=output, forms=forms)
