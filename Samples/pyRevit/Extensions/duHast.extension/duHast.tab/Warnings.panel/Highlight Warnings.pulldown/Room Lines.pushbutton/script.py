"""
An extension to report in table format room separation lines in the model which have warnings associated with them.

Note:

- The output table will be displayed in the pyRevit output window.
- table contains the warnings by the design set / option phase and level the room separation lines are placed on for ease of finding the room separation lines in the model.

Usage:

- Run this script
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# room lines reporting
from solvers.warnings_reporting import (
    report_room_lines_with_warnings_by_design_option_level_phase_created,
)

report_room_lines_with_warnings_by_design_option_level_phase_created(
    doc=doc, output=output, forms=forms
)
