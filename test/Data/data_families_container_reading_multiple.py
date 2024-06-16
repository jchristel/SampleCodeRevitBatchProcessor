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


TEST_REPORT_DIRECTORY_MULTIPLE = os.path.join(
    get_directory_path_from_file_path(__file__), "ReadContainer_02"
)

import data_families_test_comparison_data as DATA


class DataReadFamiliesIntoContainers(test.Test):

    def __init__(self):
        # store document in base class
        super(DataReadFamiliesIntoContainers, self).__init__(
            test_name="read family data into multiple container instances"
        )

    def _number_of_base_entries(self, container, expected_number):
        return_value = Result()
        return_value.append_message(
            "Expecting {} family base data entries and got {}".format(
                expected_number, len(container.family_base_data_storage)
            )
        )
        try:
            assert len(container.family_base_data_storage) == expected_number
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred when checking family base data entry length: {}".format(
                    e
                ),
            )
        return return_value

    def _number_of_category_entries(self, container, expected_number):
        return_value = Result()
        return_value.append_message(
            "Expecting {} category data entries and got {}".format(
                expected_number, len(container.category_data_storage)
            )
        )
        try:
            assert len(container.category_data_storage) == expected_number
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred when checking category data entry length: {}".format(
                    e
                ),
            )
        return return_value

    def _number_of_line_pattern_entries(self, container, expected_number):
        return_value = Result()
        return_value.append_message(
            "Expecting {} line pattern data entries and got {}".format(
                expected_number, len(container.line_pattern_data_storage)
            )
        )
        try:
            assert len(container.line_pattern_data_storage) == expected_number
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred when checking line pattern data entry length: {}".format(
                    e
                ),
            )
        return return_value

    def _number_of_shared_parameter_entries(self, container, expected_number):
        return_value = Result()
        return_value.append_message(
            "Expecting {} shared parameter data entries and got {}".format(
                expected_number, len(container.shared_parameter_data_storage)
            )
        )
        try:
            assert len(container.shared_parameter_data_storage) == expected_number
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred when checking shared parameter data entry length: {}".format(
                    e
                ),
            )
        return return_value

    def _number_of_warnings_entries(self, container, expected_number):
        return_value = Result()
        return_value.append_message(
            "Expecting {} warnings data entries and got {}".format(
                expected_number, len(container.warnings_data_storage)
            )
        )
        try:
            assert len(container.warnings_data_storage) == expected_number
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred when checking warnings data entry length: {}".format(
                    e
                ),
            )
        return return_value

    def _multiple_common_asserts(self, container, test_data):
        return_value = Result()
        # print("test data", test_data)

        try:
            return_value.append_message("...Testing common properties.")

            # check family name
            return_value.append_message(
                "......Expecting family name {} and got {}".format(
                    test_data[3], container.family_name
                )
            )
            try:
                assert container.family_name == test_data[3]
            except Exception as e:
                return_value.update_sep(
                    False, "Exception in family name assessment: {}".format(e)
                )

            # check family nesting path
            return_value.append_message(
                "......Expecting family nesting path {} and got {}".format(
                    test_data[1], container.family_nesting_path
                )
            )
            try:
                assert container.family_nesting_path == test_data[1]
            except Exception as e:
                return_value.update_sep(
                    False, "Exception in family nesting path assessment: {}".format(e)
                )

            # check family category nesting path
            return_value.append_message(
                "......Expecting family category nesting path {} and got {}".format(
                    test_data[2], container.family_category_nesting_path
                )
            )
            try:
                assert container.family_category == test_data[2]
            except Exception as e:
                return_value.update_sep(
                    False,
                    "Exception in family category nesting path assessment: {}".format(
                        e
                    ),
                )

            # check is root family
            return_value.append_message(
                "......Expecting is root family {} and got {}".format(
                    True, container.is_root_family
                )
            )
            try:
                assert container.is_root_family == True
            except Exception as e:
                return_value.update_sep(
                    False, "Exception in is root family assessment: {}".format(e)
                )

            # check family file path
            return_value.append_message(
                "......Expecting family file path {} and got {}".format(
                    test_data[4], container.family_file_path
                )
            )
            try:
                assert container.family_file_path == test_data[4]
            except Exception as e:
                return_value.update_sep(
                    False, "Exception in family file path assessment: {}".format(e)
                )

            # check family category
            category_chunks = test_data[2].split("::")
            return_value.append_message(
                "......Expecting category {} and got {}".format(
                    category_chunks[-1], container.family_category
                )
            )
            try:
                assert container.family_category == category_chunks[-1]
            except Exception as e:
                return_value.update_sep(
                    False, "Exception in family category assessment: {}".format(e)
                )
        except Exception as e:
            return_value.update_sep(
                False, "Exception in basic properties assessment: {}".format(e)
            )

        return return_value

    def multiple_family_base_01(self, container):
        return_value = Result()

        if isinstance(container, FamilyDataContainer) == False:
            raise TypeError(
                "container is of type {} but expect {}".format(
                    type(container), FamilyDataContainer
                )
            )
        # container should have one entry
        test_data = [
            DATA.TEST_DATA_FAMILY_BASE[0][0],
        ]

        try:
            # check basics:
            check_basics_result = self._multiple_common_asserts(
                container=container, test_data=test_data[0]
            )
            return_value.update(check_basics_result)
            try:
                assert check_basics_result.status == True
                return_value.append_message("...Common properties are as expected.")
            except Exception as e:
                return_value.update_sep(
                    False, "Expected true , got: {}".format(check_basics_result.status)
                )

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {} when testing base properties: {}".format(
                    self.test_name, e
                ),
            )

        try:
            # check specifics
            return_value.append_message("...Checking specific properties.")
            # should have one entry only
            return_value.update(self._number_of_base_entries(container, len(test_data)))

            # check category data
            return_value.update(self._number_of_category_entries(container, 0))

            # check line pattern data
            return_value.update(self._number_of_line_pattern_entries(container, 0))

            # check shared parameter data
            return_value.update(self._number_of_shared_parameter_entries(container, 0))

            # check warnings data
            return_value.update(self._number_of_warnings_entries(container, 0))

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {} when testing specific properties: {}".format(
                    self.test_name, e
                ),
            )

        return return_value

    def multiple_family_category_01(self, container):
        """
        Test family data container with single family category data entry.

        :param container: FamilyDataContainer
        :type container: FamilyDataContainer
        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        return_value = Result()
        if isinstance(container, FamilyDataContainer) == False:
            raise TypeError(
                "container is of type {} but expect {}".format(
                    type(container), FamilyDataContainer
                )
            )
        # container should have two entries
        # the test data list can contain dummy (empty) lists, since I am only test base properties and number of entries from the first entry
        test_data = (
            [
                DATA.TEST_DATA_FAMILY_CATEGORIES[0][0],
                [],
            ],
        )

        try:
            # check basics:
            check_basics_result = self._multiple_common_asserts(
                container=container,
                test_data=test_data[0][0],  # check against first entry
            )
            return_value.update(check_basics_result)
            assert check_basics_result.status == True
            return_value.append_message("...Common properties are as expected.")
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {} when testing base properties: {}".format(
                    self.test_name, e
                ),
            )

        try:
            # check specifics
            return_value.append_message("...Checking specific properties.")
            # should have one entry only

            return_value.update(self._number_of_base_entries(container, 0))

            # check category data
            return_value.update(
                self._number_of_category_entries(container, len(test_data[0]))
            )

            # check line pattern data
            return_value.update(self._number_of_line_pattern_entries(container, 0))

            # check shared parameter data
            return_value.update(self._number_of_shared_parameter_entries(container, 0))

            # check warnings data
            return_value.update(self._number_of_warnings_entries(container, 0))

        except Exception as e:
            return_value.update_sep(
                False,
                "...An exception occurred in function {} when testing specific properties: {}".format(
                    self.test_name, e
                ),
            )

        return return_value

    def multiple_family_line_pattern_01(self, container):
        """
        Test family data container with single family line pattern data entry.

        :param container: FamilyDataContainer
        :type container: FamilyDataContainer
        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        return_value = Result()
        if isinstance(container, FamilyDataContainer) == False:
            raise TypeError(
                "container is of type {} but expect {}".format(
                    type(container), FamilyDataContainer
                )
            )
        # container should have five entries
        # the test data list can contain dummy (empty) lists, since I am only test base properties and number of entries from the first entry
        test_data = (
            [
                DATA.TEST_DATA_FAMILY_LINE_PATTERNS[0][0],
                [],
                [],
                [],
            ],
        )

        try:
            # check basics:
            check_basics_result = self._multiple_common_asserts(
                container=container,
                test_data=test_data[0][0],  # check against first entry
            )
            return_value.update(check_basics_result)
            try:
                assert check_basics_result.status == True
                return_value.append_message("...Common properties are as expected.")
            except Exception as e:
                return_value.update_sep(
                    False, "Expected true , got: {}".format(check_basics_result.status)
                )
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {} when testing base properties: {}".format(
                    self.test_name, e
                ),
            )

        try:
            # check specifics
            return_value.append_message("...Checking specific properties.")
            # should have one entry only

            return_value.update(self._number_of_base_entries(container, 0))

            # check category data
            return_value.update(self._number_of_category_entries(container, 0))

            # check line pattern data
            return_value.update(
                self._number_of_line_pattern_entries(container, len(test_data[0]))
            )

            # check shared parameter data
            return_value.update(self._number_of_shared_parameter_entries(container, 0))

            # check warnings data
            return_value.update(self._number_of_warnings_entries(container, 0))

        except Exception as e:
            return_value.update_sep(
                False,
                "...An exception occurred in function {} when testing specific properties: {}".format(
                    self.test_name, e
                ),
            )

        return return_value

    def multiple_family_shared_parameters_01(self, container):
        """
        Test family data container with single family shared parameter data entry.

        :param container: FamilyDataContainer
        :type container: FamilyDataContainer
        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        return_value = Result()
        if isinstance(container, FamilyDataContainer) == False:
            raise TypeError(
                "container is of type {} but expect {}".format(
                    type(container), FamilyDataContainer
                )
            )
        # container should have five entries
        # the test data list can contain dummy (empty) lists, since I am only test base properties and number of entries from the first entry
        test_data = (
            [
                DATA.TEST_DATA_SHARED_PARAMETERS[0][0],
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                [],
                [],
            ],
        )

        try:
            # check basics:
            check_basics_result = self._multiple_common_asserts(
                container=container,
                test_data=test_data[0][0],  # check against first entry
            )
            return_value.update(check_basics_result)
            try:
                assert check_basics_result.status == True
                return_value.append_message("...Common properties are as expected.")
            except Exception as e:
                return_value.update_sep(
                    False, "Expected true , got: {}".format(check_basics_result.status)
                )
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {} when testing base properties: {}".format(
                    self.test_name, e
                ),
            )

        try:
            # check specifics
            return_value.append_message("...Checking specific properties.")
            # should have one entry only

            return_value.update(self._number_of_base_entries(container, 0))

            # check category data
            return_value.update(self._number_of_category_entries(container, 0))

            # check line pattern data
            return_value.update(self._number_of_line_pattern_entries(container, 0))

            # check shared parameter data
            return_value.update(
                self._number_of_shared_parameter_entries(container, len(test_data[0]))
            )

            # check warnings data
            return_value.update(self._number_of_warnings_entries(container, 0))

        except Exception as e:
            return_value.update_sep(
                False,
                "...An exception occurred in function {} when testing specific properties: {}".format(
                    self.test_name, e
                ),
            )

        return return_value

    def multiple_family_warnings_01(self, container):
        """
        Test family data container with single family warnings data entry.

        :param container: FamilyDataContainer
        :type container: FamilyDataContainer
        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        return_value = Result()
        if isinstance(container, FamilyDataContainer) == False:
            raise TypeError(
                "container is of type {} but expect {}".format(
                    type(container), FamilyDataContainer
                )
            )
        # container should have five entries
        # the test data list can contain dummy (empty) lists, since I am only test base properties and number of entries from the first entry
        test_data = (
            [
                DATA.TEST_DATA_FAMILY_WARNINGS[0][0],
            ],
        )

        try:
            # check basics:
            check_basics_result = self._multiple_common_asserts(
                container=container,
                test_data=test_data[0][0],  # check against first entry
            )
            return_value.update(check_basics_result)
            try:
                assert check_basics_result.status == True
                return_value.append_message("...Common properties are as expected.")
            except Exception as e:
                return_value.update_sep(
                    False, "Expected true , got: {}".format(check_basics_result.status)
                )
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {} when testing base properties: {}".format(
                    self.test_name, e
                ),
            )

        try:
            # check specifics
            return_value.append_message("...Checking specific properties.")
            # should have one entry only

            return_value.update(self._number_of_base_entries(container, 0))

            # check category data
            return_value.update(self._number_of_category_entries(container, 0))

            # check line pattern data
            return_value.update(self._number_of_line_pattern_entries(container, 0))

            # check shared parameter data
            return_value.update(self._number_of_shared_parameter_entries(container, 0))

            # check warnings data
            return_value.update(
                self._number_of_warnings_entries(container, len(test_data[0]))
            )

        except Exception as e:
            return_value.update_sep(
                False,
                "...An exception occurred in function {} when testing specific properties: {}".format(
                    self.test_name, e
                ),
            )

        return return_value

    def multiple_family_base_01(self, container):
        return_value = Result()

        if isinstance(container, FamilyDataContainer) == False:
            raise TypeError(
                "container is of type {} but expect {}".format(
                    type(container), FamilyDataContainer
                )
            )
        # container should be amongst these entries
        test_data = DATA.TEST_DATA_FAMILY_BASE

        # get comparison string from container.
        if len(container.family_base_data_storage) != 1:
            raise ValueError(
                "wrong number of base data storage in container: [{}]".format(
                    len(container.family_base_data_storage)
                )
            )

        comp_string = container.family_base_data_storage[
            0
        ].get_data_values_as_list_of_strings()

        # check if comparison string is in test data
        if comp_string in test_data[0]:
            return_value.append_message("Found match for container")
        else:
            return_value.update_sep(
                False,
                "Container {} {} has no match in test data.".format(
                    container.family_nesting_path,
                    container.family_category_nesting_path,
                ),
            )

        #  check other container properties
        try:
            # check specifics
            return_value.append_message("...Checking specific properties.")
            # should have one entry only
            return_value.update(self._number_of_base_entries(container, 1))

            # check category data
            return_value.update(self._number_of_category_entries(container, 0))

            # check line pattern data
            return_value.update(self._number_of_line_pattern_entries(container, 0))

            # check shared parameter data
            return_value.update(self._number_of_shared_parameter_entries(container, 0))

            # check warnings data
            return_value.update(self._number_of_warnings_entries(container, 0))

        except Exception as e:
            return_value.update_sep(
                False,
                "...An exception occurred in function {} when testing specific properties: {}".format(
                    self.test_name, e
                ),
            )

        return return_value

    def _run_tests(self, test_data, test_files_directory):
        """
        actual test runner
        """
        return_value = Result()
        # test reports
        for test_file, test_result in test_data.items():
            return_value.append_message(
                "\n" + "Reading test file: [{}]".format(test_file)
            )
            try:
                # read overall family data
                family_base_data_result = read_data_into_family_containers(
                    os.path.join(test_files_directory, test_file)
                )
                return_value.append_message("..." + family_base_data_result.message)
            except Exception as e:
                return_value.update_sep(
                    False,
                    "An exception occurred when reading test file {} {}".format(
                        test_file, e
                    ),
                )
                continue

            # processing status
            return_value.append_message(
                "...expecting status: {} and got: {}".format(
                    test_result[0], family_base_data_result.status
                )
            )
            assert family_base_data_result.status == test_result[0]

            # number of container instances
            return_value.append_message(
                "...expecting number of containers: {} and got: {}".format(
                    test_result[1], len(family_base_data_result.result)
                )
            )
            assert len(family_base_data_result.result) == test_result[1]

            # run specific tests
            if len(test_result[2]) > 0:
                test_counter = 0
                for test_function in test_result[2]:
                    test_counter += 1
                    return_value.append_message(
                        "Running specific tests. \n...{} of {} for {}".format(
                            test_counter, len(test_result[2]), test_file
                        )
                    )
                    container_counter = 0
                    for container in family_base_data_result.result:
                        container_counter += 1
                        return_value.append_message(
                            "...[[container counter]] {}".format(container_counter)
                        )
                        test_result = test_function(container)
                        return_value.update(test_result)
                        if test_result.status:
                            return_value.append_message(
                                "Specific tests passed for [{}].".format(test_file)
                            )
            else:
                return_value.append_message(
                    "No specific tests to run for [{}].".format(test_file)
                )

    def test(self):
        """
        Reads family data reports into multiple containers.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        return_value = Result()
        try:

            # test multiple families per report
            # 4 test files
            test_files_multiple = {
                "": (True, 1, []),
                "FamilyBaseDataCombinedReport_multiple.csv": (
                    True,
                    5,
                    [self.multiple_family_base_01],
                ),
                "FamilyCategoriesCombinedReport_multiple.csv": (
                    True,
                    3,
                    [],
                ),
                "FamilyLinePatternsCombinedReport_multiple.csv": (
                    True,
                    4,
                    [],
                ),
                "FamilySharedParametersCombinedReport_multiple.csv": (
                    True,
                    4,
                    [],
                ),
                "FamilyWarningsCombinedReport_multiple.csv": (True, 5, []),
            }

            # run tests
            test_result_multiple = self._run_tests(
                test_data=test_files_multiple,
                test_files_directory=TEST_REPORT_DIRECTORY_MULTIPLE,
            )

            return_value.update(test_result_multiple)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {} : {}".format(self.test_name, e),
            )
        return return_value.status, return_value.message
