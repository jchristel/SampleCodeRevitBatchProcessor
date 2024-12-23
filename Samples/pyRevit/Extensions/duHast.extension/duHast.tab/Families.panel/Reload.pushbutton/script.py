"""
An extension to bulk reload families from a library directory into a project file.

This extension uses Revit's failure handling mechanism to suppress warnings and errors during the re-load process.
Note: 

By default the families will be loaded using:

    - overwrite existing parameter values in project from family
    - use shared sub components already in project

Match Status:
Matches in the library are identified by family name only. The scroipt will search the library directory and all it's subdirectories for a match.

Match status: ok

    - Only families with a single match in the library directory are eligible for reload. 

Match status multiple matches found:

    - There are multiple files in the library matching a family. Cant be reloaded.

Match status:

    - No match for that family was found.

Usage:

- Run the script.
- Select all families you want to reload (check the check box).
- press "Reload"

- Right click on a column header will bring up a filter menu.
- single click on a column header will sort families by this column
- to change the library path, paste a new path into the text box

"""

# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

# reload families
from families.reload.reloader import reloaded_families_entry

reloaded_families_entry(doc=doc, output=output, forms=forms)