"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family report data utility module containing functions to read the data from file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reads family base data into two list of named tuples.

rootFamily:

- name 
- category 
- filePath 


nestedFamily:

- name 
- category 
- filePath 
- rootPath  [str]
- categoryPath [str]

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from collections import namedtuple

from duHast.Utilities.Objects import result as res
from duHast.Utilities import files_csv as fileCSV, files_io as fileIO
from duHast.Revit.Family.Data.family_base_data_utils_deprecated import (
    read_overall_family_data_list,
)

# tuples containing base family data read from file
rootFamily = namedtuple("rootFamily", "name category filePath")
nestedFamily = namedtuple(
    "nestedFamily", "name category filePath rootPath categoryPath"
)

# row structure of report data file
BASE_DATA_LIST_INDEX_ROOT_PATH = 0
BASE_DATA_LIST_INDEX_ROOT_CATEGORY_PATH = 1
BASE_DATA_LIST_INDEX_FAMILY_NAME = 2
BASE_DATA_LIST_INDEX_FAMILY_FILE_PATH = 3

# exceptions
EXCEPTION_NO_FAMILY_BASE_DATA_FILES = "Report data list files do not exist."
EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES = "Empty report data list file!"

# ------------------------------------- combining reports --------------------------------------------


def _get_data_rows_from_dictionary(dic):
    """
    Builds list of data rows from dictionary past in

    :param dic: Dictionary where key is a tuple and values is a list of list of strings
    :type dic: {named tuple: [[str]]}
    :param dataList: List of list of strings
    :type dataList: [[str]]

    :return: List of list of strings
    :rtype: [[str]]
    """
    print(dic)
    dataList = []
    # get rows from dictionary
    for k, v in dic.items():
        # get data rows for root family
        for rootData in v[0]:
            dataList.append(rootData.report_data)
        # get data rows for any nested families
        for nestedFamRowValue in v[1]:
            dataList.append(nestedFamRowValue.report_data)
    return dataList


def _compare_family_dictionaries(previous_aggregated_data, new_aggregated_data):
    """
    Compares two aggregate data dictionaries. Any new root family from newAgData ( root family occurring in newAgData only) will be add to the previousAgData dictionary.
    Any existing root family (root family occurring in previous and new aggregate data dictionaries) will be updated in the previousAgData dictionary with row data from the newAgData data dictionary.


    :param previous_aggregated_data: A dictionary containing aggregated family data from the previous report.
    :type previous_aggregated_data: {key:str, value ([str],[str])}
    :param new_aggregated_data: A dictionary containing aggregated family data from the new report.
    :type new_aggregated_data: {key:str, value ([str],[str])}
    :return:

        If previous_aggregated_data is empty and new_aggregated_data contains data, new_aggregated_data will be returned unchanged.
        If new_aggregated_data is empty and previous_aggregated_data contains data, previous_aggregated_data will be returned unchanged.
        if both dictionary are empty an empty dictionary will be returned.

    :rtype: {key:str, value ([str],[str])}
    """

    return_value = res.Result()
    # check corner cases:
    if len(new_aggregated_data) == 0 and len(previous_aggregated_data) > 0:
        # new is empty, but previous has data
        return_value.update_sep(
            True, "New report data is empty, using previous report data only"
        )
        return_value.result.append(previous_aggregated_data)
    elif len(new_aggregated_data) > 0 and len(previous_aggregated_data) == 0:
        # new has data, but previous is empty
        return_value.update_sep(
            True, "Previous report data is empty, using new report data only"
        )
        return_value.result.append(new_aggregated_data)
    elif len(new_aggregated_data) == 0 and len(previous_aggregated_data) == 0:
        # new is empty, previous is empty
        return_value.update_sep(
            True, "Previous report data and new report data are empty!"
        )
        return_value.result.append({})
    else:
        # other and current have data
        for family_path, family_data in new_aggregated_data.items():
            if family_path in previous_aggregated_data:
                return_value.append_message(
                    "Substituting family data: {}".format(family_path)
                )
            else:
                return_value.append_message(
                    "Adding new family data: {}".format(family_path)
                )
            previous_aggregated_data[family_path] = new_aggregated_data[family_path]
        return_value.result.append(previous_aggregated_data)
    return return_value


def _get_nested_families_belonging_to_root_families(root_family, nested_families):
    """
    Returns a list of all row data of nested families belonging to a given root family.

    :param rootFam: A tuple of a root family from a report.
    :type rootFam: tuple of type 'rootFamily'
    :param nestedFamilies: A list of tuples of all nested families in a report
    :type nestedFamilies: [tuple of type 'nestedFamily']

    :return:
    :rtype: _type_
    """

    nested_families_belonging_to_root_families = []
    for nested_family in nested_families:
        if (
            root_family.name == nested_family.rootPath[0]
            and root_family.category == nested_family.categoryPath[0]
        ):
            nested_families_belonging_to_root_families.append(
                nested_families[nested_family][0]
            )
            print("nested family in list", nested_families[nested_family][0])
        else:
            print(
                "root family name: [{}] root family category: [{}] nested family root path: [{}] nested family category path: [{}]".format(
                    root_family.name,
                    root_family.category,
                    nested_family.rootPath[0],
                    nested_family.categoryPath[0],
                )
            )
    return nested_families_belonging_to_root_families


def _aggregate_family_data(root_families, nested_families):
    """
    Returns a dictionary where key are all the root family file path from a report and value is a tuple of two list of strings containing
    the row data read from report file for the root family itself (first list) and the row data read from report file for any nested families (second list).

    :param rootFamilies: A list containing tuples of all root families in a report.
    :type rootFamilies: [tuple of type 'rootFamily']
    :param nestedFamilies: A list of tuples of all nested families in a report
    :type nestedFamilies: [tuple of type 'nestedFamily']

    :return: Returns a dictionary where key is the root family file path and value is a tuple of root family at index zero and nested families at index 1
    :rtype: {key:str, value (root family,[nested families])}
    """

    # key is root family, value is tuple of csv row representing the root family data and list of rows each representing a nested family data
    aggregated_family_data = {}
    for root_family in root_families:
        nested_families_of_root_family_row_data = (
            _get_nested_families_belonging_to_root_families(
                root_family, nested_families
            )
        )
        # key is the unique family file path of the root family
        # value is a tuple of two lists : root  at index 0, nested fam at index 1
        aggregated_family_data[root_family.filePath] = (
            root_family,
            nested_families_of_root_family_row_data,
        )
    return aggregated_family_data


def _check_families_still_exist(family_data):
    """
    Checks whether families still exist on file server.

    Reason why families no longer exist:

    - family got deleted or moved
    - family got renamed

    :param famData: A dictionary containing aggregated family data from the a report.
    :type famData: {key:str, value ([str],[str])}

    :return:
        Result class instance.

        - .status True if successfully removed any outdated family data or None needed removing. Otherwise False.
        - .message will contain list of families removed or message nothing needed to be removed.
        - . result will contain past in dictionary at index 0

        On exception:

        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        remove_keys = []
        # get keys from dic as a list
        # check which ones do not exist anymore
        for file_path in family_data.keys():
            if fileIO.file_exist(file_path) == False:
                remove_keys.append(file_path)

        # check if any family requires to be removed from the data set
        if len(remove_keys) > 0:
            # remove those keys from dictionary
            for key in remove_keys:
                remove_single_key = family_data.pop(key, None)
                if remove_single_key != None:
                    return_value.append_message(
                        "Removed family from data: {}".format(key)
                    )
                else:
                    return_value.append_message(
                        "Failed to removed family from data: {}".format(key)
                    )
        else:
            return_value.append_message("No family required removing from data.")

        # update return data
        return_value.update_sep(True, "Successfully updated family data.")
        return_value.result.append(family_data)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to check whether families still exist with exception: {}".format(e),
        )
    return return_value


def combine_reports(previous_report_path, new_report_path):
    """
    This combines two reports by:

    - building an aggregate data dictionary of each report (key root family file path, values lists containing the row data read from file for the root family as well as any nested families)
    - comparing the previous report dictionary with the new report dictionary and
        - adding any new families found in the new report dictionary
        - updating any previous report families found with data matching the root family in the new report dictionary

    All reports start with the following 2 columns:
    root	rootCategory

    First entry (after split at separator) in each of these columns identifies root family uniquely.
    Assume that new report only ever adds or substitutes entries in previous report but does not delete from it!

    This function checks at the end whether families still exist on file server. If not, they will be removed from the data set.

    :param previous_report_path: A fully qualified file path to the previous report file.
    :type previous_report_path: str
    :param new_report_path: A fully qualified file path to the new report file.
    :type new_report_path: str

    :return: list of lists of report rows
    :rtype: [[str]]
    """

    return_value = res.Result()
    # read families from both reports
    # ...compare them:
    # take all families from current report and all none matching families from the other report

    previous_aggregated_families = {}
    new_aggregated_families = {}

    print("reading previous")
    # previous report
    try:
        previous_root, previous_nested = read_overall_family_data_list(
            previous_report_path
        )
        # previous_root, previous_nested = read_unique_families_with_row_data_from_report(
        #    previous_report_path
        # )
        return_value.append_message(
            "Previous report: found {} root families.".format(len(previous_root))
        )
        return_value.append_message(
            "Previous report: found {} nested families.".format(len(previous_nested))
        )
        # build dictionary containing all family data per root family
        previous_aggregated_families = _aggregate_family_data(
            previous_root, previous_nested
        )
    except Exception as e:
        # check whether empty file exception
        if str(e) != EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES:
            raise e

    print("reading new")
    # new report
    try:
        new_root, new_nested = read_overall_family_data_list(new_report_path)
        # new_root, new_nested = read_unique_families_with_row_data_from_report(
        #    new_report_path
        # )
        # build dictionary containing all family data per root family
        new_aggregated_families = _aggregate_family_data(new_root, new_nested)
        return_value.append_message(
            "New report: found {} root families.".format(len(new_root)) + ""
        )
        return_value.append_message(
            "New report: found {} nested families.".format(len(new_nested)) + ""
        )
    except Exception as e:
        # check whether empty file exception
        if str(e) != EXCEPTION_EMPTY_FAMILY_BASE_DATA_FILES:
            raise e

    print("comparing")
    # compare dictionaries: build unique list of families
    unique_family_data_status = _compare_family_dictionaries(
        previous_aggregated_families, new_aggregated_families
    )
    return_value.update(unique_family_data_status)
    unique_family_data = unique_family_data_status.result[0]

    print("checking")
    # check whether families still exist on file server
    remove_none_existing_families = _check_families_still_exist(unique_family_data)
    return_value.update(remove_none_existing_families)
    # only update family data if culling occurred without any exceptions
    if remove_none_existing_families.status:
        unique_family_data = remove_none_existing_families.result[0]

    # get report header row (there should be a previous report file...otherwise this will write an empty header row)
    header_row = fileCSV.get_first_row_in_csv_file(previous_report_path)
    # header_row = header.split(",")
    print("building")
    # build list of data rows
    rows_current = _get_data_rows_from_dictionary(unique_family_data)
    # sort rows by root ( first entry ) since other code (circ reference checker for instance) expects data sorted
    rows_current.sort()
    # start with header row
    rows_current.insert(0, header_row)
    # overwrite return result value since it is already containing data from previous operations
    return_value.result = rows_current
    return return_value
