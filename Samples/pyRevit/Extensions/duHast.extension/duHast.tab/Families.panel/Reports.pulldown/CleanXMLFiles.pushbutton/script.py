"""
An extension deleteing xml files (part atom exports) in the library location that do not have a matching family file.

Usage:

- Run the script.

    - The report will be displayed in the output window.


"""


# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# delete unused xml files
from families.clean_part_atom_library import clean_part_atom_exports_in_library_entry

clean_part_atom_exports_in_library_entry(doc=doc, output=output, forms=forms)