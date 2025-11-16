"""
An extension to export catalogue files based on XML atom export. 
Refer to: ExtractPartAtomFromFamilyFile Method of the Application object
https://www.revitapidocs.com/2024/1f2c631b-2733-0aa7-051c-42bccb07f05e.htm

WIP:
- This script will export catalogue files as XML files.
- The script will than create a new catalogue file based on the XML file.
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# export catalogue files

# import grids and bubbles from library
from families.exportCatalogueFile.export_catalogue_file import export_catalogue_file_entry

# export it baby!
export_catalogue_file_entry(doc=doc, output=output, forms=forms)
