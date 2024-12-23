"""
An extension to report in table format area lines in the model which have warnings associated with them.

Note:

- The output table will be displayed in the pyRevit output window.
- table contains the warnings by area scheme and the level they are placed on, and list of area views associated with that area scheme and level for ease of finding the area lines in the model.

Usage:

- Run this script
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# report area lines with warnings
from solvers.warnings_reporting import (
    report_area_lines_with_warnings_by_scheme_and_level,
)

report_area_lines_with_warnings_by_scheme_and_level(doc=doc, output=output, forms=forms)
