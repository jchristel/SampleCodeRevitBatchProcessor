"""
An extension reporting on differences between families in the any number of libraries.

A report per library is created by the `report_families_in_library` function.

The report includes:

    - family name
    - family type name
    - family category
    - specific family type parameters
    - an entry per library with the value of the parameter or N/A if the family, or family type or parameter does not exist in the library.

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

# compare families in libraries
from families.compare_library_reports import compare_library_reports_entry

compare_library_reports_entry(doc=doc, output=output, forms=forms)