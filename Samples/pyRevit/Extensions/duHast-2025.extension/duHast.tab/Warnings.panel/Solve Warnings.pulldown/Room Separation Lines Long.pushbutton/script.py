"""
An extension to solve room separation lines overlap warnings by extending the longer of the two overlapping lines to the extend of the smaller of the two lines and then deleting the smaller line.


Note:

- This will ignore any warnings where 

    - one of the overlapping lines is within a group
    - both overlapping lines are within a group
    - one of the overlapping lines is a room separation line and the other is a wall
    - both overlapping lines are not within the same design option
    - both overlapping lines are not within the same phase
    
Usage:

- Run this script
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# room lines overlap -> long
from solvers.warnings_solvers import solve_duplicate_room_separation_lines_long

solve_duplicate_room_separation_lines_long(doc=doc, output=output, forms=forms)
