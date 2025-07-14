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

# provide some statistics on the push it elements in the model by design set and option
from pushIt_associated. statistics_by_designset_and_option import push_it_design_set_options_by_id

push_it_design_set_options_by_id(doc=doc, uiapp = uiapp, output=output, forms=forms)