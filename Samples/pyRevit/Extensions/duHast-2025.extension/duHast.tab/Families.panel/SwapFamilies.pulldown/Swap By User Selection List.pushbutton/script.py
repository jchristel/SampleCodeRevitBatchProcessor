"""
An extension setting swapping out family instances of types based on user selection.

Usage:

- Run the script.

    - the script will ask the user to select a type of a family and following on that to select a target type.
    - Families instances which can be swapped will be swapped out.
    - families which are nested or in groups will be reported.

"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# create default catalogue type in family
from families.swap_by_user_selection import swap_instances_by_user_selection_entry

swap_instances_by_user_selection_entry(doc=doc, output=output, forms=forms)