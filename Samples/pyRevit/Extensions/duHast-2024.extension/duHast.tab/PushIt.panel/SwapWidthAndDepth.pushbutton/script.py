"""
An extension used to swap the width and depth value of instance driven mock room families

Usage:

- Run the script.

    - select the family or families to swap the width and depth values for

"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# create default catalogue type in family
from pushIt_associated.swap_width_and_depth import swap_width_and_depth_entry

swap_width_and_depth_entry(doc=doc, uiapp = uiapp, output=output, forms=forms)