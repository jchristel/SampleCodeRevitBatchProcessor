"""
An extension used to display some basic stats on push it elements in the model.

Usage:

- Run the script.


"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc
uiapp = __revit__

# create default catalogue type in family
from pushIt_associated.statistics import basic_stats_entry

basic_stats_entry(doc=doc, uiapp = uiapp, output=output, forms=forms)