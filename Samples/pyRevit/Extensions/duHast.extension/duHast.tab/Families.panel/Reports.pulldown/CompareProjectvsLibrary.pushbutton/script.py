"""
An extension reporting on families in a project file compared to families in a library.
Only differences between the two are reported.

The report includes:

    - family name
    - family type name
    - family category
    - specific family type parameters and their values

Usage:

- Run the script.

    - The report will be displayed in the output window.

- Select a location to where to save the csv file.
- press "Save"

"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# compare families in library against families in project
from families.compare_loaded_vs_library import compare_loaded_families_vs_library_entry

compare_loaded_families_vs_library_entry(doc=doc, output=output, forms=forms)