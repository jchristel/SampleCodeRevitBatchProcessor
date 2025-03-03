"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing comparison reporting of family types in a project vs in a library functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reports:

- if family does not exist in library
- if type does not exist in library
- if a parameter value for a given type is different to the parameter value for that type in the library

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

import os

from Autodesk.Revit.DB import Family

from duHast.Revit.Family.family_types_get_data_from_xml import get_family_type_data_from_library
from duHast.Revit.Family.family_types_model_get_data_from_xml import get_type_data_via_XML_from_family_object
from duHast.Revit.Family.family_functions import get_name_to_family_dict
from duHast.Utilities.files_xml import get_all_xml_files_from_directories
from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects.result import Result
from duHast.UI.Objects.ProgressBase import ProgressBase
from duHast.Revit.Family.Data.Objects.family_type_data_storage_manager import (
    FamilyTypeDataStorageManager,
)


def get_family_type_data_from_project_file(
    doc, type_data_from_library, progress_callback=None
):
    """
    Get the family type data from the families in the project file of families that are in the library only.

    :param doc: Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param type_data_from_library: list of family type data from the library
    :type type_data_from_library: [:class:`FamilyTypeDataStorageManager`]
    :param progress_callback: progress callback object
    :type progress_callback: :class:`ProgressBase`

    :return:
        Result class instance.

        - result.status: XML conversion status will be returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain which xml file was read and converted into family type data.
        - result.result will be [:class:`FamilyTypeDataStorageManager`]

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list

    :rtype: :class:`.Result`
    """

    return_value = Result()
    matched_data = []
    try:

        # get all families in the project
        families_loaded = get_name_to_family_dict(doc)

        # set progress counter
        counter = 1
        max_value_xml = len(families_loaded)

        # loop over loaded families and search for matches based on name and category
        for fam_name, revit_family in families_loaded.items():

            # update progress
            if progress_callback:
                progress_callback.update(counter, max_value_xml,fam_name)

            # check this is a family
            if isinstance(revit_family, Family) is False:
                return_value.append_message(
                    "skipping family: {} as it is not a family".format(fam_name)
                )
                continue

            # ignore in place families
            if revit_family.IsInPlace:
                continue

            # get the family category
            fam_cat = revit_family.FamilyCategory.Name

            # get the family type data storage from the library
            found_match = False
            match_library = None
            for type_data_storage_manager_library in type_data_from_library:
                if (
                    type_data_storage_manager_library.family_type_data_storage[
                        0
                    ].family_name
                    == fam_name
                    and type_data_storage_manager_library.family_type_data_storage[
                        0
                    ].root_category_path
                    == fam_cat
                ):
                    # found a match...
                    found_match = True
                    match_library = type_data_storage_manager_library
                    break

            # check if match in library was found
            if found_match is False:
                # no match found
                matched_data.append(([fam_name, fam_cat], None))
                # update progress
                counter = counter + 1
                continue

            # create temp xml files from loaded family
            type_data_result = get_type_data_via_XML_from_family_object(
                revit_family=revit_family
            )
            if type_data_result.status == False:
                return_value.update_sep(
                    False,
                    "Failed to get type data from family: {} with exception: {}".format(
                        fam_name, type_data_result.message
                    ),
                )
                matched_data.append((type_data_storage_manager_loaded_fam, None))
                # update progress
                counter = counter + 1
                continue

            # get the type data of the family
            type_data_storage_manager_loaded_fam = type_data_result.result[0]
            # add to matched data
            matched_data.append((type_data_storage_manager_loaded_fam, match_library))

            # update progress
            counter = counter + 1

            # check for user cancel
            if progress_callback != None:
                if progress_callback.is_cancelled():
                    return_value.append_message("User cancelled!")
                    break

    except Exception as e:
        return_value.update_sep(
            False, "Failed to gather family data with exception: {}".format(e)
        )

    # store data to be returned
    return_value.result = matched_data

    return return_value


def build_comparison_report(type_data_matches, ignore_list_path):
    """
    Build a comparison report of the family type data from the project file against the library.
    Only differences are reported.

    :param type_data_matches: list of matched family type data
    :type type_data_matches: [([:class:`FamilyTypeDataStorageManager`], [:class:`FamilyTypeDataStorageManager`])]
    :param ignore_list_path: path to a csv file containing a list of families to ignore (name, category) in the comparison report.
    :type ignore_list_path: str

    :return:
        Result class instance.

        - result.status: Comparison status will be returned in result.status. False if an exception occurred, otherwise True.
        - result.message: will be empty.
        - result.result will be [[str]] where each entry is a list of family name, category etc and difference.

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list

    :rtype: :class:`.Result`
    """

    # families not found in library, used to avoid duplicate entries
    not_in_library = []
    # list of differences
    diff = []
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
        for entry in type_data_matches:
            fam_name = ""
            fam_category = ""
            # set a flag that the family export from revit project file resulted in no types exported
            family_export_has_types = False

            # get name and category ( for non matched family this may just be a list of name and category rather than a storage object)
            if isinstance(entry[0], list):
                fam_name = entry[0][0]
                fam_category = entry[0][1]
            elif isinstance(entry[0], FamilyTypeDataStorageManager):
                fam_name = entry[0].family_name
                fam_category = entry[0].family_category
                # there is a chance that the family export from the project file contains no types
                if entry[0].family_has_types:
                    # set flag that types were exported
                    family_export_has_types = True
            else:
                raise ValueError(
                    "entry[0] is not a list or FamilyTypeDataStorageManager: {}".format(
                        type(entry[0])
                    )
                )

            # check if the family is in ignore list based on name and category
            ignore = False
            for ignore_entry in ignore_data:
                if ignore_entry[0] == fam_name and ignore_entry[1] == fam_category:
                    ignore = True
                    break
            if ignore:
                continue

            if entry[1] == None:
                if "{}{}".format(fam_name, fam_category) not in not_in_library:
                    not_in_library.append("{}{}".format(fam_name, fam_category))
                    # family not found in library
                    diff.append([fam_name, fam_category, "No match in library"])
                continue
            elif family_export_has_types == False:
                # family has no types
                diff.append(
                    [fam_name, fam_category, "Family in project has no types exported"]
                )
            else:
                # compare the two data sets
                diff = diff + entry[0].get_difference(entry[1])

    except Exception as e:
        return_value.update_sep(
            False, "Failed to gather family data with exception: {}".format(e)
        )

    # store data to be returned
    return_value.result = diff

    return return_value


def compare_family_files_in_project_against_library(
    doc, process_directories, ignore_list_path=None, progress_callback=None
):
    """
    Compare the family type data from the project file against the library.
    Only differences are reported.

    :param doc: Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param process_directories: list of directories to search for xml files
    :type process_directories: list
    :param ignore_list_path: path to a csv file containing a list of families to ignore (name, category) in the comparison report.
    :type ignore_list_path: str
    :param progress_callback: progress callback object
    :type progress_callback: :class:`ProgressBase`

    :return:
        Result class instance.

        - result.status: Comparison status will be returned in result.status. False if an exception occurred, otherwise True.
        - result.message: Log entries.
        - result.result will be [[str]] where each entry is a list of family name, category etc and difference.

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list

    :rtype: :class:`.Result`
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

    try:

        # get all xml files from the directory representing families in the library (point of truth)
        xml_files_in_libraries = get_all_xml_files_from_directories(process_directories)

        # check if any xml files were found
        if len(xml_files_in_libraries) == 0:
            return_value.update_sep(
                False,
                "No XML files found in the directories: {}".format(process_directories),
            )
            return_value.append_message(t.stop())
            return return_value
        
        return_value.append_message(
            "Found {} XML files in the directories: {}".format(
                len(xml_files_in_libraries), process_directories
            )
        )

        # get the type data from the library
        type_data_from_library_result = get_family_type_data_from_library(
            xml_files_in_libraries, progress_callback
        )

        # check if the type data from the library was successfully gathered
        if (
            type_data_from_library_result.status == False
            or len(type_data_from_library_result.result) == 0
        ):
            return_value.update_sep(False, type_data_from_library_result.message)
            return_value.append_message(t.stop())
            return return_value
        
        return_value.append_message(
            "Successfully gathered family type data from the library."
        )

        # get type data from the family files in project file
        type_data_from_project_result = get_family_type_data_from_project_file(
            doc, type_data_from_library_result.result, progress_callback
        )

        # check if the type data from the project file was successfully gathered
        if (
            type_data_from_project_result.status == False
            or len(type_data_from_project_result.result) == 0
        ):
            return_value.update_sep(False, type_data_from_project_result.message)
            return_value.append_message(t.stop())
            return return_value
        
        return_value.append_message(
            "Successfully gathered family type data from the project file."
        )

        # compare the data
        comparison_report_result = build_comparison_report(
            type_data_from_project_result.result, ignore_list_path
        )
        if comparison_report_result.status == False:
            return_value.update_sep(False, comparison_report_result.message)
            return_value.append_message(t.stop())
            return return_value
        
        return_value.append_message(
            "Successfully compared family type data from project file against library."
        )
        return_value.append_message(t.stop())

        # store the comparison report as sorted list by family name
        sorted_list = sorted(comparison_report_result.result, key=lambda x: x[0])

        # add the file name the family is in as the first entry
        for entry in sorted_list:
            entry.insert(0, os.path.basename(doc.Title))

        return_value.result = sorted_list

    except Exception as e:
        return_value.update_sep(
            False, "Failed to gather family data with exception: {}".format(e)
        )
        if t.is_running():
            return_value.append_message(t.stop())

    return return_value
