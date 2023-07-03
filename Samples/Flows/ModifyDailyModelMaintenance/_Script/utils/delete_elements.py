"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing delete elements functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- delete line pattern starting with IMPORT
- delete duplicate BVN line patterns
- delete unused elevation markers
- delete unwanted shared parameters


"""
# import Autodesk
import Autodesk.Revit.DB as rdb

# import common library
import settings as settings  # sets up all commonly used variables and path locations!

import duHast.Utilities.Objects.result as res
from duHast.Utilities.files_csv import read_csv_file
from duHast.Revit.LinePattern.line_patterns import (
    delete_line_pattern_starts_with,
    delete_line_patterns_contains,
    delete_duplicate_line_patter_names,
)
from duHast.Revit.Views.delete import delete_unused_elevation_view_markers
from duHast.Revit.SharedParameters.shared_parameters_delete import (
    delete_shared_parameters,
)


def delete_line_pattern_starting_with_import(doc, revit_file_path, output):
    """
    Write deletes any line patterns created from cad import

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    """

    return_value = res.Result()
    output("Deleting line pattern where names starts with IMPORT...start")
    task_value = delete_line_pattern_starts_with(doc, "IMPORT")
    return_value.update(task_value)
    return return_value


def delete_bvn_duplicate_patterns(doc, revit_file_path, output):
    """
    Deletes all line patterns ending on BVN1* to BVN9*

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    """

    return_value = res.Result()
    output("Deleting line pattern where names ends with BVN1* to BVN9*...start")
    # loop over integers 1 to 10 to get all duplicates
    for x in range(1, 10):
        task_value = delete_line_patterns_contains(doc, "BVN" + str(x))
        return_value.update(task_value)
    return return_value


def delete_unused_elev_view_markers(doc, revit_file_path, output):
    """
    Deletes unused elevation markers

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    """

    return_value = res.Result()
    output("Deleting unused elevation markers...start")
    task_value = delete_unused_elevation_view_markers(doc)
    return_value.update(task_value)
    return return_value


def delete_unwanted_shared_parameters(doc, revit_file_path, output):
    """
    Deletes all shared paras in a project file flagged as unwanted

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    """

    return_value = res.Result()
    output("Deleting unwanted shared parameters...start")
    # read data file
    file_data = read_csv_file(
        settings.SCRIPT_DIRECTORY + "\\" + settings.UNWANTED_SHARED_PARAMETER_FILE
    )
    guids_to_delete = []
    for row in file_data:
        if len(row) > 1:
            if len(row[1]) == 36:
                guids_to_delete.append(row[1])
        else:
            return_value.update_sep(
                False, "Shared parameter file contains malformed row: {}".format(row)
            )
    if len(guids_to_delete) > 0:
        result_delete = delete_shared_parameters(doc, guids_to_delete)
        return_value.update(result_delete)
    else:
        return_value.update_sep(
            False,
            "No valid GUIDS found in guid data file: {}".format(
                settings.SCRIPT_DIRECTORY + "\\" + settings.UNWANTED_SHARED_PARAMETER_FILE
            ),
        )
    return return_value


def delete_duplicate_line_pattern_names(doc, revit_file_path, output):
    """
    Deletes line patterns with duplicate names, keeping the one with the smallest id (oldest)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_file_path: _description_
    :type revit_file_path: _type_
    :return: _description_
    :rtype: _type_
    """

    return_value = res.Result()
    output("Deleting duplicate line pattern names...start")
    task_value = delete_duplicate_line_patter_names(doc)
    return_value.update(task_value)
    return return_value
