"""
An extension to clean up catalogue files.

This script will remove all parameters from a catalogue file that are: 

- instance parameters
- type parameters driven by a formula

The script will also sort the parameters:

- first by parameters defined in: 
- the balance will be sorted alphabetically.

Usage:

- Export the catalogue file to a folder using the "Export Family Types" command in Revit.
- With the family file open, run this script:

    - Select the catalogue file.
    - Click "Open".
    - the script will list which parameters (columns) will be removed from the catalogue file.
    - The script will show a table view of the revised catalogue file written to file.
    - The revised catalogue file will be saved to the same folder as the original catalogue file but with a suffix: __.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# clean up catalogue files

# import grids and bubbles from library
from families.cleanupCatalogueFiles.cleaner import clean_up_catalogue_file

# clean it baby!
clean_up_catalogue_file(doc=doc, output=output, forms=forms)
