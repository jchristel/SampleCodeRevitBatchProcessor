"""
An extension setting up a default type referring to a catalogue file and deleting all other types in a family.

Usage:

- Run the script.

"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# create default catalogue type in family
from families.defaultCatalogueFileType import default_catalogue_file_type_entry

default_catalogue_file_type_entry(doc=doc, output=output, forms=forms)