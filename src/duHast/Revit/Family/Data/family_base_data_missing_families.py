"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Base data analysis module containing functions to find missing families.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A missing family is a family which is not present in the family base data report as a root family but present as a nested family.

Algorithm description:

- read base data file processing list

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects import result as res
from duHast.Revit.Family.Data.family_data_family_processor_utils import process_data


def get_unique_nested_families_from_path_data(path_data):
    # path data is a list of tuples list[(family_name_nesting, family_category_nesting)] or None

    # will be a list of tuples 0: family name, 1 family category
    unique_nested_families = []

    # loop over all unique nesting path
    for entry in path_data:
        family_name_nesting = entry[0]
        category_name_nesting = entry[1]
        if len(family_name_nesting) != len(category_name_nesting):
            raise ValueError(
                "Name path length: {} is different to category path length: {}".format(
                    len(family_name_nesting), len(category_name_nesting)
                )
            )
        # loop over each entry in path ignoring the first entry (root family)
        for i in range(1, len(entry[0])):
            test_value = (family_name_nesting[i], category_name_nesting[i])
            if test_value not in unique_nested_families:
                unique_nested_families.append(test_value)

    return unique_nested_families


def get_unique_root_families_from_family_data(family_data):
    # family data is a list of family_data_family instances

    # will be a list of tuples 0: family name, 1 family category
    unique_root_families = []

    for family in family_data:
        test_data = (family.family_name, family.family_category)
        if test_data not in unique_root_families:
            unique_root_families.append(test_data)
        else:
            raise ValueError("Duplicated root family found: {}".format(test_data))

    return unique_root_families


def get_missing_families(root_families, nested_families):
    # root_families and nested_families is a list of tuples in format 0: family name, 1: family category

    missing_families = []

    for nested in nested_families:
        if nested not in root_families:
            missing_families.append(nested)

    return missing_families


def process_families(family_data, result_list):
    """
    Function to retrieve longest unique nesting path data from families.

    :param family_data: list of family data objects
    :type family_data: list
    :param result_list: list to store longest unique path
    :type result_list: list[(family_name_nesting, family_category_nesting)]
    :return: list of tuples containing family name nesting at 0 and family category nesting at 1
    """

    # loop over all family data
    for family in family_data:
        # process each family
        family.process()
        longest_path = family.get_longest_unique_nesting_path()
        if longest_path != None:
            for lp in longest_path:
                result_list.append((family, lp))
    return result_list


def _find_missing_families(families, families_longest_path):
    """
    Returns a list of tuples representing nested family name and category which does not have a matching root family.

    :param families: List of family instances
    :type families: []
    :param families_longest_path: list of tuples representing longest unique name nesting path and matching longest unique category nesting path
    :type families_longest_path: []
    :return: List of tuples representing the name and category of a family missing (from the library and therefore not presented as root family)
    :rtype: [(family name, family category)]
    """

    missing_families = []
    # process longest path retrieved into unique families
    unique_nested_families = get_unique_nested_families_from_path_data(
        families_longest_path
    )

    # process family data and get unique names+ categories
    unique_root_families = get_unique_root_families_from_family_data(families)

    # check which nested families do not exist as root families
    missing_families = get_missing_families(
        root_families=unique_root_families, nested_families=unique_nested_families
    )

    return missing_families


def check_families_missing_from_library(family_base_data_report_file_path):
    """
    Processes a family base data report and identifies any nested families which have not been processed as a root family\
        and therefore do not exist in the library.
    
    :param family_base_data_report_file_path: Fully qualified file path to family base data report file. 
    :type family_base_data_report_file_path: str
    
    :return: 
        Result class instance.

        - result.status. True if missing families where found without an exception occurring.
        - result.message will contain the summary messages of the process including time stamps.
        - result.result [(nested_family_name, nested_family_category)]
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    # read families into data family objects
    # check for duplicate family names in nesting tree

    return_value = res.Result()

    # set up a timer
    t_process = Timer()
    t_process.start()

    try:

        # start timer again
        t_process.start()

        # load and process families
        families_processed = process_data(
            family_base_data_report_file_path=family_base_data_report_file_path,
            do_this=process_families,
        )

        # check if processing was successful, otherwise get out
        if families_processed.status == False:
            raise ValueError(families_processed.message)

        # get results
        families = families_processed.result[0]
        families_longest_path = families_processed.result[1]

        return_value.append_message(
            "{} Found: {} unique longest path in families.".format(
                t_process.stop(), len(families_longest_path)
            )
        )

        # start timer again
        t_process.start()

        # get tuples representing missing root family name and Revit category
        missing_families = _find_missing_families(
            families=families, families_longest_path=families_longest_path
        )

        return_value.append_message(
            "Found {} missing families. {}".format(
                len(missing_families), t_process.stop()
            )
        )
        if len(missing_families) > 0:
            return_value.result = missing_families

    except Exception as e:
        return_value.update_sep(
            False,
            "An error occurred while finding missing families: {}".format(e),
        )

    return return_value


# ----------------------------missing families: direct host files -----------------------------------------


def get_direct_root_families(families, missing_families):

    # return value
    direct_host_families = []

    # loop over families and check for match at nesting level 01
    for family in families:
        # families at nesting level 1
        if 1 in family.nesting_by_level:
            for family_at_level_one in family.nesting_by_level[1]:
                # build test value: a tuple made up of the family name and family category
                test_value = (
                    family_at_level_one.family_name,
                    family_at_level_one.family_category,
                )
                if test_value in missing_families:
                    # match found...
                    direct_host_families.append(family_at_level_one)

    return direct_host_families


def find_missing_families_direct_host_families(family_base_data_report_file_path):
    """
    Returns a list of FamilyDataFamily instances which represent the direct parents (host families) of the missing families.

    :param family_base_data_report_file_path: Fully qualified file path to family base data report file.
    :type family_base_data_report_file_path: str

    :return:
        Result class instance.

        - result.status. True if host families of missing families where found without an exception occurring.
        - result.message will contain the summary messages of the process including time stamps.
        - result.result [:class:`.FamilyDataFamily`]

        On exception:

        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    # read families into data family objects
    # check for duplicate family names in nesting tree

    return_value = res.Result()

    # set up a timer
    t_process = Timer()
    t_process.start()

    try:

        # start timer again
        t_process.start()

        # load and process families
        families_processed_result = process_data(
            family_base_data_report_file_path=family_base_data_report_file_path,
            do_this=process_families,
        )

        # check if processing was successful, otherwise get out
        if families_processed_result.status == False:
            raise ValueError(families_processed_result.message)

        # get results
        families = []
        families_longest_path = []
        for nested_tuple in families_processed_result.result:
            # per nested path there might be multiple entries of the same family
            if nested_tuple[0] not in families:
                families.append(nested_tuple[0])
            families_longest_path.append(nested_tuple[1])

        return_value.append_message(
            "{} Found: {} unique longest path in families.".format(
                t_process.stop(), len(families_longest_path)
            )
        )

        # start timer again
        t_process.start()

        # get tuples representing missing root family name and Revit category
        missing_families = _find_missing_families(
            families=families, families_longest_path=families_longest_path
        )

        # get the direct root families of nested families identified as missing
        direct_root_families = []
        if len(missing_families) > 0:
            # loop over longest path and find the ones where the second entry in the nesting path is a missing family
            direct_root_families = get_direct_root_families(
                families=families,
                missing_families=missing_families,
            )

            return_value.append_message(
                "Found {} direct hosts to missing families. {}".format(
                    len(direct_root_families), t_process.stop()
                )
            )
        else:
            return_value.append_message("No missing root families found in data set.")

        # update result property as required
        if len(direct_root_families) > 0:
            return_value.result = direct_root_families

    except Exception as e:
        return_value.update_sep(
            False,
            "An error occurred while finding missing families direct host families: {}".format(
                e
            ),
        )

    return return_value
