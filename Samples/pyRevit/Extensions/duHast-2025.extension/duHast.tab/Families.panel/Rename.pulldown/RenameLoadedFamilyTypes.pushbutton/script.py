"""
An extension to bulk rename families loaded in a project.

Usage:

- create a csv file with the following columns:
   
    - Current family name: with out the file extension
    - File path	: fully qualified file path to the family file. ( can be left blank when renaming families within a project )
    - Family category: the Revit category of the family.
    - old family type name
    - new family type name

    Note:

    - First row is treated as a header row and its content is ignored.

- Run the script.
- Select the csv file you created.
- press "Rename"

"""

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# rename loaded family types

# import from library
#from families.rename.rename_loaded_familes import rename_loaded_families

# rename loaded families!
#rename_loaded_families(doc=doc, output=output, forms=forms)

print("Oh, hi there!")