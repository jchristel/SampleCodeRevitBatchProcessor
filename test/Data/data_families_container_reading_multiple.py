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

from duHast.Revit.Family.Data.Objects.family_base_data_storage import (
    FamilyBaseDataStorage,
)
from duHast.Revit.Categories.Data.Objects.category_data_storage import (
    FamilyCategoryDataStorage,
)
from duHast.Revit.LinePattern.Data.Objects.line_pattern_data_storage import (
    FamilyLinePatternDataStorage,
)
from duHast.Revit.SharedParameters.Data.Objects.shared_parameter_data_storage import (
    FamilySharedParameterDataStorage,
)
from duHast.Revit.Warnings.Data.Objects.warnings_data_storage import (
    FamilyWarningsDataStorage,
)

TEST_REPORT_DIRECTORY_MULTIPLE = os.path.join(
    get_directory_path_from_file_path(__file__), "ReadContainer_02"
)

# required to import a module from the same directory
TEST_DIR = os.path.join(get_directory_path_from_file_path(__file__))
sys.path += [
    TEST_DIR,
]

# test data
import data_families_test_comparison_data as DATA


class DataReadFamiliesIntoContainers(test.Test):

    def __init__(self):
        # store document in base class
        super(DataReadFamiliesIntoContainers, self).__init__(
            test_name="read multiple family data into multiple container instances"
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
        # container should be amongst these entries
        test_data = DATA.TEST_DATA_FAMILY_BASE[0]

        # get comparison string from container.
        if len(container.family_base_data_storage) != 1:
            raise ValueError(
                "wrong number of base data storage in container: [{}]".format(
                    len(container.family_base_data_storage)
                )
            )

        # check if comparison string is in test data
        comp_string = container.family_base_data_storage[
            0
        ].get_data_values_as_list_of_strings()

        # check if comparison string is in test data
        # and count the rows that match
        found_match = False
        # row counter is later on used to check number of storage entries
        row_counter = 0
        for row in test_data:
            if "".join(row) == "".join(comp_string):
                row_counter += 1
                found_match = True

        if found_match:
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
            return_value.update(self._number_of_base_entries(container, row_counter))

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
        # container should be amongst these entries
        test_data = DATA.TEST_DATA_FAMILY_CATEGORIES[0]

        # get comparison string from container.
        if len(container.category_data_storage) == 0:
            raise ValueError(
                "wrong number of category data storage in container: [{}]".format(
                    len(container.category_data_storage)
                )
            )

        # check if comparison string is in test data
        comp_row = container.category_data_storage[
            0
        ].get_data_values_as_list_of_strings()

        # just get the first few entries
        comp_row_string = "".join(comp_row[:4])

        # check if comparison string is in test data
        # and count the rows that match
        found_match = False
        # row counter is later on used to check number of storage entries
        row_counter = 0
        for row in test_data:
            # just get the first few entries
            row_string = "".join(row[:4])
            if row_string == comp_row_string:
                row_counter += 1
                found_match = True

        if found_match:
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
            return_value.update(self._number_of_base_entries(container, 0))

            # check category data
            return_value.update(
                self._number_of_category_entries(container, row_counter)
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
        # container should be amongst these entries
        test_data = DATA.TEST_DATA_FAMILY_LINE_PATTERNS[0]

        # get comparison string from container.
        if len(container.line_pattern_data_storage) == 0:
            raise ValueError(
                "wrong number of line pattern data storage in container: [{}]".format(
                    len(container.line_pattern_data_storage)
                )
            )

        # check if comparison string is in test data
        comp_row = container.line_pattern_data_storage[
            0
        ].get_data_values_as_list_of_strings()

        # just get the first few entries
        comp_row_string = "".join(comp_row[:4])

        # check if comparison string is in test data
        # and count the rows that match
        found_match = False
        # row counter is later on used to check number of storage entries
        row_counter = 0
        for row in test_data:
            # just get the first few entries
            row_string = "".join(row[:4])
            if row_string == comp_row_string:
                row_counter += 1
                found_match = True

        if found_match:
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
            return_value.update(self._number_of_base_entries(container, 0))

            # check category data
            return_value.update(self._number_of_category_entries(container, 0))

            # check line pattern data
            return_value.update(
                self._number_of_line_pattern_entries(container, row_counter)
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
        # container should be amongst these entries
        test_data = DATA.TEST_DATA_FAMILY_SHARED_PARAMETERS[0]

        # get comparison string from container.
        if len(container.shared_parameter_data_storage) == 0:
            raise ValueError(
                "wrong number of line pattern data storage in container: [{}]".format(
                    len(container.shared_parameter_data_storage)
                )
            )

        # check if comparison string is in test data
        comp_row = container.shared_parameter_data_storage[
            0
        ].get_data_values_as_list_of_strings()

        # just get the first few entries
        comp_row_string = "".join(comp_row[:4])

        # check if comparison string is in test data
        # and count the rows that match
        found_match = False
        # row counter is later on used to check number of storage entries
        row_counter = 0
        for row in test_data:
            # just get the first few entries
            row_string = "".join(row[:4])
            if row_string == comp_row_string:
                row_counter += 1
                found_match = True

        if found_match:
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
            return_value.update(self._number_of_base_entries(container, 0))

            # check category data
            return_value.update(self._number_of_category_entries(container, 0))

            # check line pattern data
            return_value.update(self._number_of_line_pattern_entries(container, 0))

            # check shared parameter data
            return_value.update(
                self._number_of_shared_parameter_entries(container, row_counter)
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
        # container should be amongst these entries
        test_data = DATA.TEST_DATA_FAMILY_WARNINGS[0]

        # get comparison string from container.
        if len(container.warnings_data_storage) == 0:
            raise ValueError(
                "wrong number of base data storage in container: [{}]".format(
                    len(container.warnings_data_storage)
                )
            )

        # check if comparison string is in test data
        comp_string = container.warnings_data_storage[
            0
        ].get_data_values_as_list_of_strings()

        # check if comparison string is in test data
        # and count the rows that match
        found_match = False
        # row counter is later on used to check number of storage entries
        row_counter = 0
        for row in test_data:
            if "".join(row) == "".join(comp_string):
                row_counter += 1
                found_match = True

        if found_match:
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
            return_value.update(self._number_of_base_entries(container, 0))

            # check category data
            return_value.update(self._number_of_category_entries(container, 0))

            # check line pattern data
            return_value.update(self._number_of_line_pattern_entries(container, 0))

            # check shared parameter data
            return_value.update(self._number_of_shared_parameter_entries(container, 0))

            # check warnings data
            return_value.update(
                self._number_of_warnings_entries(container, row_counter)
            )

        except Exception as e:
            return_value.update_sep(
                False,
                "...An exception occurred in function {} when testing specific properties: {}".format(
                    self.test_name, e
                ),
            )

        return return_value

    def multiple_family_all_01(self, container):
        """
        Test family data container with multiple data entries for all properties.

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

        # get all the test data as a dictionary
        data_dict = DATA.build_data_dict_all()

        # get the container key
        container_key = container.family_nesting_path
        if container_key not in data_dict:
            raise ValueError(
                "Container key {} not found in test data.".format(container_key)
            )

        # get all the test data as a dictionary for this container
        test_data_container = data_dict[container_key]

        # check base data
        if FamilyBaseDataStorage.data_type in test_data_container:
            test_data_base = test_data_container[FamilyBaseDataStorage.data_type]
            try:
                assert len(container.family_base_data_storage) == len(test_data_base)

                return_value.append_message(
                    "Expecting {} family base data entries and got {}".format(
                        len(test_data_base),
                        len(container.family_base_data_storage),
                    )
                )
            except Exception as e:
                return_value.update_sep(
                    False,
                    "An exception occurred when checking base data entry length: {}. Expecting {} family base data entries and got {}".format(
                        e,
                        len(test_data_base),
                        len(container.family_base_data_storage),
                    ),
                ),
        else:
            try:
                assert len(container.family_base_data_storage) == 0
                return_value.append_message(
                    "Expecting 0 family base data entries and got {}".format(
                        len(container.family_base_data_storage)
                    )
                )
            except Exception as e:
                return_value.update_sep(
                    False,
                    "An exception occurred when checking base data entry length: {}. Expecting 0 family base data entries and got {}".format(
                        e, len(container.family_base_data_storage)
                    ),
                )

        # check category data
        if FamilyCategoryDataStorage.data_type in test_data_container:
            test_data_categories = test_data_container[
                FamilyCategoryDataStorage.data_type
            ]
            try:
                assert len(container.category_data_storage) == len(test_data_categories)
                return_value.append_message(
                    "Expecting {} category data entries and got {}".format(
                        len(test_data_categories), len(container.category_data_storage)
                    )
                )
            except Exception as e:
                return_value.update_sep(
                    False,
                    "An exception occurred when checking category data entry length: {}".format(
                        e
                    ),
                )
        else:
            try:
                assert len(container.category_data_storage) == 0
                return_value.append_message(
                    "Expecting 0 category data entries and got {}".format(
                        len(container.category_data_storage)
                    )
                )
            except Exception as e:
                return_value.update_sep(
                    False,
                    "An exception occurred when checking category data entry length: {}".format(
                        e
                    ),
                )

        # check line pattern data
        if FamilyLinePatternDataStorage.data_type in test_data_container:
            test_data_line_patterns = test_data_container[
                FamilyLinePatternDataStorage.data_type
            ]
            try:
                assert len(container.line_pattern_data_storage) == len(
                    test_data_line_patterns
                )
                return_value.append_message(
                    "Expecting {} line pattern data entries and got {}".format(
                        len(test_data_line_patterns),
                        len(container.line_pattern_data_storage),
                    )
                )
            except Exception as e:
                return_value.update_sep(
                    False,
                    "An exception occurred when checking line pattern data entry length: {}".format(
                        e
                    ),
                )
        else:
            try:
                assert len(container.line_pattern_data_storage) == 0
                return_value.append_message(
                    "Expecting 0 line pattern data entries and got {}".format(
                        len(container.line_pattern_data_storage)
                    )
                )
            except Exception as e:
                return_value.update_sep(
                    False,
                    "An exception occurred when checking line pattern data entry length: {}".format(
                        e
                    ),
                )

        # check shared parameter data
        if FamilySharedParameterDataStorage.data_type in test_data_container:
            test_data_shared_parameters = test_data_container[
                FamilySharedParameterDataStorage.data_type
            ]
            try:
                assert len(container.shared_parameter_data_storage) == len(
                    test_data_shared_parameters
                )
                return_value.append_message(
                    "Expecting {} shared parameter data entries and got {}".format(
                        len(test_data_shared_parameters),
                        len(container.shared_parameter_data_storage),
                    )
                )
            except Exception as e:
                return_value.update_sep(
                    False,
                    "An exception occurred when checking shared parameter data entry length: {}".format(
                        e
                    ),
                )
        else:
            try:
                assert len(container.shared_parameter_data_storage) == 0
                return_value.append_message(
                    "Expecting 0 shared parameter data entries and got {}".format(
                        len(container.shared_parameter_data_storage)
                    )
                )
            except Exception as e:
                return_value.update_sep(
                    False,
                    "An exception occurred when checking shared parameter data entry length: {}".format(
                        e
                    ),
                )

        # check warnings data
        if FamilyWarningsDataStorage.data_type in test_data_container:
            test_data_warnings = test_data_container[
                FamilyWarningsDataStorage.data_type
            ]
            try:
                assert len(container.warnings_data_storage) == len(test_data_warnings)
                return_value.append_message(
                    "Expecting {} warnings data entries and got {}".format(
                        len(test_data_warnings), len(container.warnings_data_storage)
                    )
                )
            except Exception as e:
                return_value.update_sep(
                    False,
                    "An exception occurred when checking warnings data entry length: {}".format(
                        e
                    ),
                )
        else:
            try:
                assert len(container.warnings_data_storage) == 0
                return_value.append_message(
                    "Expecting 0 warnings data entries and got {}".format(
                        len(container.warnings_data_storage)
                    )
                )
            except Exception as e:
                return_value.update_sep(
                    False,
                    "An exception occurred when checking warnings data entry length: {}".format(
                        e
                    ),
                )

        return return_value

    def _run_tests(self, test_data, test_files_directory):
        """
        actual test runner
        """
        return_value = Result()
        # test reports
        try:
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
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function run tests : {}".format(e),
            )
        return return_value

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
                "": (True, 5, [self.multiple_family_all_01]),
                "FamilyBaseDataCombinedReport_multiple.csv": (
                    True,
                    5,
                    [self.multiple_family_base_01],
                ),
                "FamilyCategoriesCombinedReport_multiple.csv": (
                    True,
                    3,
                    [self.multiple_family_category_01],
                ),
                "FamilyLinePatternsCombinedReport_multiple.csv": (
                    True,
                    4,
                    [self.multiple_family_line_pattern_01],
                ),
                "FamilySharedParametersCombinedReport_multiple.csv": (
                    True,
                    4,
                    [self.multiple_family_shared_parameters_01],
                ),
                "FamilyWarningsCombinedReport_multiple.csv": (
                    True,
                    5,
                    [self.multiple_family_warnings_01],
                ),
            }

            # run tests
            test_result_multiple = self._run_tests(
                test_data=test_files_multiple,
                test_files_directory=TEST_REPORT_DIRECTORY_MULTIPLE,
            )

            return_value.update(test_result_multiple)

            return_value.status = False
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {} : {}".format(self.test_name, e),
            )
        return return_value.status, return_value.message
