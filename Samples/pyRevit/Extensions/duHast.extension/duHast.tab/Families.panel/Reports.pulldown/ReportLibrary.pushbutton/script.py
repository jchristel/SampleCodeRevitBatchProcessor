"""
An extension reporting on families in a library directory.

The report includes:

    - family name
    - family type name
    - family category
    - all family type parameters and their values


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

# reporting families in library
from families.report_families_in_library_xml import report_families_in_library_entry

report_families_in_library_entry(doc=doc, output=output, forms=forms)