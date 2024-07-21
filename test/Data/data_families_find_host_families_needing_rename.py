"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains data read from file tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#


import os
import sys

from test.utils import test

from duHast.Revit.Family.Data.family_base_data_utils_deprecated import (
    nested_family,
    find_root_families_not_in_nested_data,
    read_overall_family_data_list_from_directory,
)
from duHast.Revit.Family.Data.family_rename_find_host_families import (
    find_host_families_with_nested_families_requiring_rename,
)
from duHast.Utilities.files_io import get_directory_path_from_file_path

TEST_REPORT_DIRECTORY_ONE = os.path.join(get_directory_path_from_file_path(__file__), "RenameTest_01")
TEST_REPORT_DIRECTORY_TWO = os.path.join(get_directory_path_from_file_path(__file__), "RenameTest_02")
TEST_REPORT_DIRECTORY_THREE = os.path.join(get_directory_path_from_file_path(__file__), "RenameTest_03")


class DataFindHostFamiliesWithFamiliesToRename(test.Test):

    def __init__(self):
        # store document in base class
        super(DataFindHostFamiliesWithFamiliesToRename, self).__init__(
            test_name="find_host_families_with_families_to_rename"
        )

    def test(self):
        """
        Finds host families containing families needed to be renamed in the overall family report.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "-"

        test_data = {
            "test_one": (TEST_REPORT_DIRECTORY_ONE, []),
            "test_two": (
                TEST_REPORT_DIRECTORY_TWO,
                [
                    "Sample_Family_Eight",
                    "Sample_Family_Eleven",
                    "Sample_Family_Five",
                    "Sample_Family_Four",
                    "Sample_Family_Nine",
                    "Sample_Family_One",
                    "Sample_Family_Seven",
                    "Sample_Family_Six",
                    "Sample_Family_Three",
                    "Sample_Family_Two",
                ],
            ),
            "test_three": (
                TEST_REPORT_DIRECTORY_THREE,
                [
                    "Sample_Family_Nine",
                    "Sample_Family_One",
                    "Sample_Family_Six",
                    "Sample_Family_Two",
                ],
            ),
        }
        try:

            # run through tests
            for test in test_data:
                message += "\n\nRunning test: {}".format(test)
                result_search = (
                    find_host_families_with_nested_families_requiring_rename(
                        test_data[test][0]
                    )
                )

                if result_search.status == False:
                    flag = False
                    message += "\n{}".format(result_search.message)
                    return flag, message

                host_families = result_search.result

                # set up expected result
                expected_result_family_names = test_data[test][1]

                # sort result by name
                sort_by_name = sorted(host_families, key=lambda x: x.name)
                sorted_host_family_names_from_data = [x.name for x in sort_by_name]

                # check if the result is as expected
                message += "\nresult from data {}: {} \nvs \nexpected: {}".format(
                    test,
                    "\n".join(sorted_host_family_names_from_data),
                    "\n".join(sorted(expected_result_family_names)),
                )

                assert "\n".join(sorted_host_family_names_from_data) == "\n".join(
                    sorted(expected_result_family_names)
                )

        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + (
                    "An exception occurred in function {} : {}".format(
                        self.test_name, e
                    )
                )
            )
        return flag, message
