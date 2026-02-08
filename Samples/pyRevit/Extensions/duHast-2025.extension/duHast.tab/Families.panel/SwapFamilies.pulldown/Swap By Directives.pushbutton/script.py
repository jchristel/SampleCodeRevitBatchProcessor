"""
An extension setting swapping out family instances of types based on directives.

Usage:

- Run the script.

    - the script will ask to select a csv file contianing the directives.
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
from families.swap_by_directives import swap_instances_by_directives_entry

swap_instances_by_directives_entry(doc=doc, output=output, forms=forms)