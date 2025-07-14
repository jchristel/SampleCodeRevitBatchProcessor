"""
An extension to bulk load families from a directory.

This extension uses Revit's failure handling mechanism to suppress warnings and errors during the loading process.


Usage:

- Place the families you want to load in a directory and subdirectories.
- Run the script.
- Select the directory.
- Click "Open".
- The script will load the families into the project.

"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# loading families en mass
print("Oh hey, I'm bulk loading families!")
from families.bulk_load import load_families_entry

load_families_entry(doc=doc, output=output, forms=forms)
