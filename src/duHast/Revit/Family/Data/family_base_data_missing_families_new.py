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

import threading
import os

from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects import result as res
from duHast.Revit.Family.Data.family_report_reader import read_data_into_families


def get_unique_nested_families_from_path_data(path_data):
    pass


def get_unique_root_families_from_family_data(family_data):
    pass


def get_missing_families(root_families, nested_families):
    pass


def process_data():
    pass

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
                result_list.append(lp)
    return result_list


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
        - result.result [nestedFamily]
        
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
        # read families into data
        read_result = read_data_into_families(family_base_data_report_file_path)

        return_value.update(read_result)
        return_value.append_message(
            "Number of family instances: {} read {}.".format(
                len(read_result.result),
                t_process.stop(),
            )
        )

        # start timer again
        t_process.start()

        # check if something went wrong
        if not read_result.status:
            raise ValueError(read_result.message)
        elif len(read_result.result) == 0:
            raise ValueError(
                "No family data found in file: {}".format(
                    family_base_data_report_file_path
                )
            )

        # process each family so unique path are created
        # results will be stored in here:
        families_longest_path = []

        # set up some multithreading
        core_count = int(os.environ["NUMBER_OF_PROCESSORS"])
        if core_count > 2:
            return_value.append_message("cores: ".format(core_count))
            # leave some room for other processes
            core_count = core_count - 1
            chunk_size = len(read_result.result) / core_count
            threads = []
            # set up threads
            for i in range(core_count):
                t = threading.Thread(
                    target=process_families,
                    args=(
                        read_result.result[i * chunk_size : (i + 1) * chunk_size],
                        families_longest_path,
                    ),
                )
                threads.append(t)
            # start up threads
            for t in threads:
                t.start()
            # wait for results
            for t in threads:
                t.join()
        else:
            # no threading
            families_longest_path = process_families(read_result.result)

        return_value.append_message(
            "{} Found: {} unique longest path in families.".format(
                t_process.stop(), len(families_longest_path)
            )
        )

        # process longest path retrieved into unique families
        unique_nested_families = get_unique_nested_families_from_path_data(
            families_longest_path
        )

        # process family data and get unique names+ categories
        unique_root_families = get_unique_root_families_from_family_data(
            read_result.result
        )

        # check which nested families do not exist as root families
        missing_families = get_missing_families(
            root_families=unique_root_families, nested_families=unique_nested_families
        )

        return_value.append_message("Found {} missing families".format(len(missing_families)))
        if len(missing_families) > 0:
            return_value.result = missing_families

    except Exception as e:
        return_value.update_sep(
            False,
            "An error occurred while finding missing families: {}".format(
                e
            ),
        )

    return return_value


# ----------------------------missing families: direct host files -----------------------------------------


def find_missing_families_direct_host_families(
    familyBaseDataReportFilePath, missingFamilies
):
    """
    Returns a list of root family tuples which represent the direct parents (host families) of the missing families.

    :param missingFamilies: A list of tuple containing nested family data representing missing families(no base root family entry)
    :type missingFamilies: [nestedFamily]
    :param familyBaseDataReportFilePath: Fully qualified file path to family base data report file.
    :type familyBaseDataReportFilePath: str

    :return:
        Result class instance.

        - result.status. True if host families of missing families where found without an exception occurring.
        - result.message will contain the summary messages of the process including time stamps.
        - result.result [rootFamily]

        On exception:

        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    # loop over missing families
    # loop over base nested data
    #   - check if missing fam is in root path (name and category) if so:
    #   - get the direct parent (make sure missing family isn't first entry!)
    #   - check if direct parent is already in dictionary (key is name + category) ? if not:
    #       - add direct parent to dictionary
    #
    # loop over direct host data:
    #   - loop over root fam data and check for match in name and category; If so:
    #       - add to root family data to be returned.

    returnValue = res.Result()
    try:
        # set up a timer
        tProcess = Timer()
        tProcess.start()

        returnValue = res.Result()
        # read overall family base data from file
        (
            overallFamilyBaseRootData,
            overallFamilyBaseNestedData,
        ) = rFamBaseDataUtils.read_overall_family_data_list(
            familyBaseDataReportFilePath
        )
        returnValue.append_message(
            "{} Read overall family base data report. {} root entries found and {} nested entries found.".format(
                tProcess.stop(),
                len(overallFamilyBaseRootData),
                len(overallFamilyBaseNestedData),
            )
        )

        tProcess.start()
        hostFamilies = rFamBaseDataUtils.find_all_direct_host_families(
            missingFamilies, overallFamilyBaseNestedData
        )
        # get the root families from host family data
        rootHosts = rFamBaseDataUtils.find_root_families_from_hosts(
            hostFamilies, overallFamilyBaseRootData
        )
        returnValue.result = rootHosts
        returnValue.append_message(
            "{} Found direct host families of missing families: {}".format(
                tProcess.stop(), len(rootHosts)
            )
        )
    except Exception as e:
        returnValue.update_sep(
            False,
            "Failed to retrieve host families of missing families with exception: ".format(
                e
            ),
        )
    return returnValue
