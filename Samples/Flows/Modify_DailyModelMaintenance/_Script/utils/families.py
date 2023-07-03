"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing families related functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- reload families
- rename loaded families

"""


# import common library
import settings as settings  # sets up all commonly used variables and path locations!

import duHast.Utilities.Objects.result as res
from duHast.Revit.Family.family_reload import reload_all_families
from duHast.Revit.Family.Data.family_rename_loaded_families import (
    rename_loaded_families,
)


def _check_begins(check_list, string):
    """
    checks whether past in string starts with any entry in check_list

    :param check_list: The list containing check values
    :type check_list: [str]
    :param string: a string
    :type string: str

    :return: True if striong starts with any entry in check_list, otherwise False
    :rtype: bool
    """

    for entry in check_list:
        if string.startswith(entry):
            return True
    return False


# ----------------------------------------------- reload families -----------------------------------------


def reload_families(doc, revit_file_path, output):
    """
    Reloads families from libraries (clinical, bespoke joinery, unions)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    """

    return_value = res.Result()
    if not _check_begins(settings.EXCLUDE_FILES_FROM_FAMILY_RELOAD, doc.Title):
        output("Reloading families...start")
        task_value = reload_all_families(doc, settings.PATH_TO_CLINICAL_LIBRARY, False)
        return_value.update(task_value)
        task_value = reload_all_families(
            doc, settings.PATH_TO_BESPOKE_JOINERY_LIBRARY, False
        )
        return_value.update(task_value)
        task_value = reload_all_families(doc, settings.PATH_TO_UNIONS_LIBRARY, False)
        return_value.update(task_value)
    else:
        output("Not reloading families for this file!")
        return_value.update_sep(True, "Reloading families not required.")
    return return_value


# ----------------------------------------------- rename families -----------------------------------------


def rename_families(doc, revit_file_path, output):
    """
    Rename loaded families based on rename directives used in 'The Chain'

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    """

    return_value = res.Result()
    output("Renaming loaded families...start")
    task_value = rename_loaded_families(doc, settings.SCRIPT_DIRECTORY)
    return_value.update(task_value)
    return return_value
