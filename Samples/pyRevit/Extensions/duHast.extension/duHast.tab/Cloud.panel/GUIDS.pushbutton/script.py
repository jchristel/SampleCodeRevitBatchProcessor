"""
An extension to retrieve cloud related GUIDs from the current document.

Note:

- The exported data can be used for Revit batch Processor cloud model access.

Usage:

- Run this script
- Copy and paste data into csv files if to be used with Revit Batch Processor
"""

# pyrevit stuff
from pyrevit import revit, script, forms

logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# script
from cloud.cloud_guids import get_cloud_guids_entry

# output GUID data
get_cloud_guids_entry(doc=doc, output=output, forms=forms)
