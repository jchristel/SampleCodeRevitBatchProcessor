"""
An extension used to convert a filled region to a push it room

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
from pushIt_associated.get_a_room import get_a_room_entry

print("oh, hi there!")

# duHast dev
DU_HAST_DEV = r"C:\Users\chrjx\Documents\github\SampleCodeRevitBatchProcessor\src"
sys.path.insert(0, DU_HAST_DEV)


get_a_room_entry(doc=doc, uiapp = uiapp, output=output, forms=forms)
