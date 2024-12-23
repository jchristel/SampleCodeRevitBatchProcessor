"""
An extension to bulk rename families in a library directory.

Usage:

- create a csv file with the following columns:
   
    - Current family name: with out the file extension
    - File path	: fully qualified file path to the family file.
    - Family category: the Revit category of the family. ( can be left blank when renaming files only, needs to be filled when renaming families within a project)
    - New family name: the new family name without the file extension.

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

# rename families in directory

# import from library
from families.rename.rename_families_in_folder import rename_families_in_folder

# rename files!
rename_families_in_folder(doc=doc, output=output, forms=forms)