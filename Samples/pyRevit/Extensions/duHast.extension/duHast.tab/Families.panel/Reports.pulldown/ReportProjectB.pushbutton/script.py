"""
An extension reporting on families in a project file.

The report includes:

    - family name
    - family type name
    - family category
    - specific family type parameters and their values

        - refer to variable FAMILY_PARAMETERS_TO_REPORT: a list of parameters to report on.
    
    - family instances placed by by type in model


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

# reporting families loaded into model
from families.report_familires_in_project_type_b import report_families_in_project_entry

report_families_in_project_entry(doc=doc, output=output, forms=forms)