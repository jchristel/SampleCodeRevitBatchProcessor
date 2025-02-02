"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing reporting of family types in a project functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reports:

- all family types and their type parameters values in a project

"""

# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

from Autodesk.Revit.DB import Family

from duHast.Revit.Family.family_types_model_get_data_from_xml import (
    get_type_data_via_XML_from_family_object,
)
from duHast.Revit.Family.family_functions import get_name_and_category_to_family_dict
from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects.result import Result
from duHast.UI.Objects.ProgressBase import ProgressBase


def build_type_report(doc_name, type_data, ignore_list_path):

    # list of differences
    report_data = []
    return_value = Result()
    try:

        # get ignore data
        ignore_data = []
        if ignore_list_path != None:
            ignore_data_result = read_csv_file(ignore_list_path)
            if ignore_data_result.status == False:
                return_value.update_sep(False, ignore_data_result.message)
                return return_value
            else:
                ignore_data = ignore_data_result.result

        # loop over the data and compare
        for entry in type_data:

            # check if entry is in ignore list
            ignore = False
            for ignore_entry in ignore_data:
                if (
                    entry.family_name == ignore_entry[0]
                    and entry.family_category == ignore_entry[1]
                ):
                    ignore = True
                    break

            # if not in ignore list, add to report
            if ignore:
                continue

            # add to report
            report_data = report_data + entry.get_report_data(doc_name)

    except Exception as e:
        return_value.update_sep(
            False, "Failed to build data report with exception: {}".format(e)
        )

    # store data to be returned
    return_value.result = report_data

    return return_value


def get_all_family_type_data_from_project_file(
    doc, ignore_list_path=None, progress_callback=None
):
    """
    Get all family type data from the project file.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param ignore_list_path: The path to the ignore list file. ( 2 columns csv file with family name and category name)
    :type ignore_list_path: str
    :param progress_callback: The progress callback function.
    :type progress_callback: function
    :return: The family type data.
    :rtype: list[FamilyTypeDataStorageManager]
    """

    return_value = Result()

    # check callback class
    if progress_callback and isinstance(progress_callback, ProgressBase) == False:
        raise TypeError(
            "progress_callback needs to be inherited from ProgressBase. Got : {} instead.".format(
                type(progress_callback)
            )
        )

    # set up a timer
    t = Timer()
    t.start()

    data = []
    try:

        # get all families in the project
        families_loaded = get_name_and_category_to_family_dict(doc)

        # set progress counter
        counter = 1
        max_value_xml = len(families_loaded)

        # loop over loaded families and search for matches based on name and category
        for fam_name_and_category_name, revit_family in families_loaded.items():

            # update progress
            if progress_callback:
                progress_callback.update(counter, max_value_xml)

            # check this is a family
            if isinstance(revit_family, Family) is False:
                return_value.append_message(
                    "skipping family: {} as it is not a family".format(
                        fam_name_and_category_name
                    )
                )
                continue

            # ignore in place families
            if revit_family.IsInPlace:
                continue

            # create temp xml files from loaded family
            type_data_result = get_type_data_via_XML_from_family_object(
                revit_family=revit_family
            )
            if type_data_result.status == False:
                return_value.update_sep(
                    False,
                    "Failed to get type data from family: {} with exception: {}".format(
                        fam_name_and_category_name, type_data_result.message
                    ),
                )
                continue

            # get the type data
            data = data + type_data_result.result

            # update progress
            counter = counter + 1

            # check for user cancel
            if progress_callback != None:
                if progress_callback.is_cancelled():
                    return_value.append_message("User cancelled!")
                    break

        # build report from data
        return_value.append_message(
            "Successfully gathered family data: {}".format(t.stop())
        )

        # build report
        build_report_result = build_type_report(doc.Title, data, ignore_list_path)
        # check what came back
        return_value.update_sep(
            build_report_result.status, build_report_result.message
        )
        if build_report_result.status == False:
            return return_value
        # store the report data
        return_value.result = build_report_result.result

    except Exception as e:
        return_value.update_sep(
            False, "Failed to gather family data with exception: {}".format(e)
        )
        if t.is_running():
            return_value.append_message(t.stop())

    return return_value