"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains data read into family container from file tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


import os
import sys
import json

from test.utils import test

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.Data.family_report_reader import (
    read_data_into_family_containers,
)
from duHast.Revit.Family.Data.Objects.family_data_container import FamilyDataContainer
from duHast.Utilities.files_io import get_directory_path_from_file_path

TEST_REPORT_DIRECTORY = os.path.join(
    get_directory_path_from_file_path(__file__), "ReadContainer_01"
)


class DataReadFamiliesIntoContainer(test.Test):

    def __init__(self):
        # store document in base class
        super(DataReadFamiliesIntoContainer, self).__init__(
            test_name="read family data into container"
        )

    def _single_common_asserts(self, container, test_data):
        # print("test data", test_data)
        message = "\n-"
        try:
            message = message + "\n" + "Testing common properties."
            message = (
                message
                + "\n"
                + "...Expecting family name {} and got {}".format(
                    test_data[3], container.family_name
                )
            )
            assert container.family_name == test_data[3]

            message = (
                message
                + "\n"
                + "...Expecting family nesting path {} and got {}".format(
                    test_data[1], container.family_nesting_path
                )
            )
            assert container.family_nesting_path == test_data[1]

            message = (
                message
                + "\n"
                + "...Expecting family category nesting path {} and got {}".format(
                    test_data[2], container.family_category_nesting_path
                )
            )
            assert container.family_category == test_data[2]

            message = (
                message
                + "\n"
                + "...Expecting is root family {} and got {}".format(
                    True, container.is_root_family
                )
            )
            assert container.is_root_family == True

            message = (
                message
                + "\n"
                + "...Expecting family file path {} and got {}".format(
                    test_data[4], container.family_file_path
                )
            )
            assert container.family_file_path == test_data[4]

            category_chunks = test_data[2].split("::")
            message = (
                message
                + "\n"
                + "...Expecting category {} and got {}".format(
                    category_chunks[-1], container.family_category
                )
            )
            assert container.family_category == category_chunks[-1]
        except Exception as e:
            message = message + "\n" + "Exception {}".format(e)
            return False, message
        return True, message

    def single_family_base_01(self, container):
        message = "\n-"
        if isinstance(container, FamilyDataContainer) == False:
            raise TypeError(
                "container is of type {} but expect {}".format(
                    type(container), FamilyDataContainer
                )
            )
        # container should have one entry
        test_data = [
            "FamilyBase",
            "Sample_Family_Eight",
            "Furniture Systems",
            "Sample_Family_Eight",
            r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
        ]

        try:
            # check basics:
            check_basics_result, message_basics = self._single_common_asserts(
                container=container, test_data=test_data
            )
            message = message + "\n" + message_basics
            assert check_basics_result == True
            message = message + "\n" + "Common properties are as expected."
        except Exception as e:
            message = (
                message
                + "\n"
                + "An exception occurred in function {} when testing base properties: {}".format(
                    self.test_name, e
                )
            )

        try:
            # check specifics
            # should have one entry only
            message = (
                message
                + "\n"
                + "Expecting 1 family base data entry and got {}".format(
                    len(container.family_base_data_storage)
                )
            )
            assert len(container.family_base_data_storage) == 1

            message = (
                message
                + "\n"
                + "Expecting 0 category data entry and got {}".format(
                    len(container.category_data_storage)
                )
            )
            assert len(container.category_data_storage) == 0

            message = (
                message
                + "\n"
                + "Expecting 0 line pattern data entry and got {}".format(
                    len(container.line_pattern_data_storage)
                )
            )
            assert len(container.line_pattern_data_storage) == 0

            message = (
                message
                + "\n"
                + "Expecting 0 shared parameter data entry and got {}".format(
                    len(container.shared_parameter_data_storage)
                )
            )
            assert len(container.shared_parameter_data_storage) == 0

            message = (
                message
                + "\n"
                + "Expecting 0 warnings data entry and got {}".format(
                    len(container.warnings_data_storage)
                )
            )
            assert len(container.warnings_data_storage) == 0
        except Exception as e:
            message = (
                message
                + "\n"
                + "An exception occurred in function {} when testing specific properties: {}".format(
                    self.test_name, e
                )
            )
            return False, message
        return True, message

    def single_family_category_01(self, container):
        message = "\n-"
        if isinstance(container, FamilyDataContainer) == False:
            raise TypeError(
                "container is of type {} but expect {}".format(
                    type(container), FamilyDataContainer
                )
            )
        # container should have one entry
        test_data = (
            [
                [
                    "Category",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "1",
                    [
                        {
                            "data_type": "FamilyCategoryDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 10601223,
                        }
                    ],
                    "Furniture Systems",
                    "Fixed Furniture",
                    "3674407",
                    "None",
                    "None",
                    "None",
                    "None",
                    "-1",
                    "None",
                    "1",
                    "0",
                    "0",
                    "0",
                ],
                [
                    "Category",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "0",
                    "None",
                    "Furniture Systems",
                    "<Hidden Lines>",
                    "-2009518",
                    "None",
                    "None",
                    "None",
                    "None",
                    "-1",
                    "None",
                    "3",
                    "0",
                    "0",
                    "0",
                ],
            ],
        )

        try:
            # check basics:
            print("test data 0", test_data[0][0])
            check_basics_result, message_basics = self._single_common_asserts(
                container=container,
                test_data=test_data[0][0],  # check against first entry
            )
            message = message + "\n" + message_basics
            assert check_basics_result == True
            message = message + "\n" + "Common properties are as expected."
        except Exception as e:
            message = (
                message
                + "\n"
                + "An exception occurred in function {} when testing base properties: {}".format(
                    self.test_name, e
                )
            )

        try:
            # check specifics
            # should have one entry only
            message = (
                message
                + "\n"
                + "Expecting 0 family base data entry and got {}".format(
                    len(container.family_base_data_storage)
                )
            )
            assert len(container.family_base_data_storage) == 0

            message = (
                message
                + "\n"
                + "Expecting 2 category data entry and got {}".format(
                    len(container.category_data_storage)
                )
            )
            assert len(container.category_data_storage) == 2

            message = (
                message
                + "\n"
                + "Expecting 0 line pattern data entry and got {}".format(
                    len(container.line_pattern_data_storage)
                )
            )
            assert len(container.line_pattern_data_storage) == 0

            message = (
                message
                + "\n"
                + "Expecting 0 shared parameter data entry and got {}".format(
                    len(container.shared_parameter_data_storage)
                )
            )
            assert len(container.shared_parameter_data_storage) == 0

            message = (
                message
                + "\n"
                + "Expecting 0 warnings data entry and got {}".format(
                    len(container.warnings_data_storage)
                )
            )
            assert len(container.warnings_data_storage) == 0
        except Exception as e:
            message = (
                message
                + "\n"
                + "An exception occurred in function {} when testing specific properties: {}".format(
                    self.test_name, e
                )
            )
            return False, message
        return True, message

    def test(self):
        """
        Reads family data reports into container.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        return_value = Result()
        flag = True
        message = "\n-"
        try:

            # 4 test files
            test_files = {
                # "": (True, 1, []),
                # "FamilyBaseDataCombinedReport_single.csv": (
                #    True,
                #    1,
                #    [self.single_family_base_01],
                # ),
                "FamilyCategoriesCombinedReport_single.csv": (
                    True,
                    1,
                    [self.single_family_category_01],
                ),
                # "FamilyLinePatternsCombinedReport_single.csv": (True, 1, []),
                # "FamilySharedParametersCombinedReport_single.csv": (True, 1, []),
                # "FamilyWarningsCombinedReport_single.csv": (True, 1, []),
            }

            for test_file, test_result in test_files.items():
                print("[[test_file items]]", len(test_files.items()))
                return_value.append_message(
                    "\n" + "Reading test file: [{}]".format(test_file)
                )
                print("[[test_file]]", test_file)
                try:
                    # read overall family data
                    family_base_data_result = read_data_into_family_containers(
                        os.path.join(TEST_REPORT_DIRECTORY, test_file)
                    )
                    print(
                        "[[read result containers]]",
                        len(family_base_data_result.result),
                    )
                    # print("[[read result]]", family_base_data_result)
                    return_value.append_message("..." + family_base_data_result.message)
                except Exception as e:
                    print("[[exception in reader]]", e)
                    flag = False
                    return_value.append_message(
                        "An exception occurred when reading test file {} {}".format(
                            test_file, e
                        )
                    )
                    continue

                return_value.append_message(
                    "...expecting status: {} and got: {}".format(
                        test_result[0], family_base_data_result.status
                    )
                )
                print("[[status]]", family_base_data_result.status)
                assert family_base_data_result.status == test_result[0]
                return_value.append_message(
                    "...expecting number of entries: {} and got: {}".format(
                        test_result[1], len(family_base_data_result.result)
                    )
                )
                # print("[[entries]]", len(family_base_data_result.result))
                assert len(family_base_data_result.result) == test_result[1]

                # run specific tests
                print("[[specific tests]]", test_result[2])
                if len(test_result[2]) > 0:
                    test_counter = 0
                    for test_function in test_result[2]:
                        test_counter += 1
                        print("[[test function]]", test_counter, "\n")
                        return_value.append_message(
                            "Running specific tests. {} of {} for {}".format(
                                test_counter, len(test_result[2]), test_file
                            )
                        )
                        container_counter = 0
                        for container in family_base_data_result.result:
                            container_counter += 1
                            print("[[container]]", container_counter, "\n")
                            test_result, message = test_function(container)
                            if test_result == False:
                                flag = False
                                return_value.append_message(
                                    "An exception occurred in function {} : {}".format(
                                        self.test_name, message
                                    )
                                )
                            else:
                                return_value.append_message(
                                    "Specific tests passed for [{}].".format(test_file)
                                )
                else:
                    return_value.append_message(
                        "No specific tests to run for [{}].".format(test_file)
                    )
            # flag = False
        except Exception as e:
            flag = False
            return_value.append_message(
                    "An exception occurred in function {} : {}".format(
                        self.test_name, e
                    )
                )
        return flag, return_value.message
