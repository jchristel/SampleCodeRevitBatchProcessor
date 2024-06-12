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

    def _single_common_asserts(self, container, test_data):
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

    def single_family_base_01(self, container):
        return_value = Result()

        if isinstance(container, FamilyDataContainer) == False:
            raise TypeError(
                "container is of type {} but expect {}".format(
                    type(container), FamilyDataContainer
                )
            )
        # container should have one entry
        test_data = [
            [
                "FamilyBase",
                "Sample_Family_Eight",
                "Furniture Systems",
                "Sample_Family_Eight",
                r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
            ]
        ]

        try:
            # check basics:
            check_basics_result = self._single_common_asserts(
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

    def single_family_category_01(self, container):
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
            check_basics_result = self._single_common_asserts(
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

    def single_family_line_pattern_01(self, container):
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
        test_data = (
            [
                [
                    "LinePattern",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "1",
                    [
                        {
                            "data_type": "FamilyLinePatternDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": -2009518,
                        }
                    ],
                    "Hidden 04_BVN",
                    "1428068",
                ],
                [
                    "LinePattern",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "2",
                    [
                        {
                            "data_type": "FamilyLinePatternDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": -2000530,
                        },
                        {
                            "data_type": "FamilyLinePatternDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight :: Sample_Family_Thirteen",
                            "element_id": -2000530,
                        },
                    ],
                    "Reference Plane 02_BVN",
                    "1428069",
                ],
                [
                    "LinePattern",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "2",
                    [
                        {
                            "data_type": "FamilyLinePatternDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": -2000083,
                        },
                        {
                            "data_type": "FamilyLinePatternDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight :: Sample_Family_Thirteen",
                            "element_id": -2000083,
                        },
                    ],
                    "Dash 06_BVN",
                    "1436489",
                ],
                [
                    "LinePattern",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "1",
                    [
                        {
                            "data_type": "FamilyLinePatternDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 10600768,
                        }
                    ],
                    "Dash dot",
                    "1499753",
                ],
            ],
        )

        try:
            # check basics:
            check_basics_result = self._single_common_asserts(
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

    def single_family_shared_parameters_01(self, container):
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
        test_data = (
            [
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "94e25b89-289e-43d7-bba9-c1c23be396e9",
                    "Author",
                    "118408",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 118408,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "3091b658-a4ec-4130-98c3-f9e7dfd4c071",
                    "ItemCode",
                    "1640398",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1640398,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "81cfdf2f-1f17-4a3e-a245-37a65b7b16a0",
                    "ItemDescription",
                    "1640399",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1640399,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "be50f510-c92c-4c52-9dcf-b152201710df",
                    "ItemGroup",
                    "1640401",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1640401,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "1d88889c-80d2-4aad-acbe-11076796e986",
                    "Copyright",
                    "1642131",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1642131,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "0e397bbd-a378-4824-b08a-3c03423f5545",
                    "HEIGHT_BVN",
                    "1642132",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1642132,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "980aef7a-c409-4f02-acb2-895aed435f26",
                    "DEPTH_BVN",
                    "1642133",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1642133,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "10fc5a92-3d94-4deb-b74a-23825ebce640",
                    "WIDTH_BVN",
                    "1642135",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1642135,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "6a99c82d-821c-4726-8c75-a4e0097f4441",
                    "DetailedCategory",
                    "1698538",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1698538,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "a65f6d59-9c87-44bc-866b-5644e8412a3f",
                    "ModifiedIssue",
                    "1698539",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1698539,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "bf4c7aa0-8e21-4b5c-922b-204d48970e70",
                    "Responsibility",
                    "1698541",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1698541,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "9fb538e8-0a21-47d8-aa80-79ca7db6dccc",
                    "UniqueID",
                    "1698542",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1698542,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "6cc0c155-4ff7-44e0-9ed0-2b7e49c17aeb",
                    "MOUNTING_HEIGHT_TOP_BVN",
                    "1698543",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1698543,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "f074bc9a-c650-42f4-aeb1-29de0255343f",
                    "MOUNTING_HEIGHT_US_BVN",
                    "1698544",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1698544,
                        }
                    ],
                ],
                [
                    "SharedParameter",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "c26b60fc-38e7-410b-97ce-ab7c4c36ea01",
                    "CEILING_HEIGHT_BVN",
                    "1721566",
                    "1",
                    [
                        {
                            "data_type": "FamilySharedParameterDataStorageUsedBy",
                            "root_name_path": "Sample_Family_Eight",
                            "element_id": 1721566,
                        }
                    ],
                ],
            ],
        )

        try:
            # check basics:
            check_basics_result = self._single_common_asserts(
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

    def single_family_warnings_01(self, container):
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
        test_data = (
            [
                [
                    "Warnings",
                    "Sample_Family_Eight",
                    "Furniture Systems",
                    "Sample_Family_Eight",
                    r"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles\FamilyData\combined\Furniture Systems\Sample_Family_Eight.rfa",
                    "No warnings present in family.",
                    "",
                    "None",
                    "None",
                ],
            ],
        )

        try:
            # check basics:
            check_basics_result = self._single_common_asserts(
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
                self._number_of_shared_parameter_entries(container, 0)
            )

            # check warnings data
            return_value.update(self._number_of_warnings_entries(container, len(test_data[0])))

        except Exception as e:
            return_value.update_sep(
                False,
                "...An exception occurred in function {} when testing specific properties: {}".format(
                    self.test_name, e
                ),
            )

        return return_value

    def test(self):
        """
        Reads family data reports into container.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        return_value = Result()
        message = "\n-"
        try:

            # 4 test files
            test_files = {
                "": (True, 1, []),
                "FamilyBaseDataCombinedReport_single.csv": (
                    True,
                    1,
                    [self.single_family_base_01],
                ),
                "FamilyCategoriesCombinedReport_single.csv": (
                    True,
                    1,
                    [self.single_family_category_01],
                ),
                "FamilyLinePatternsCombinedReport_single.csv": (
                    True,
                    1,
                    [self.single_family_line_pattern_01],
                ),
                "FamilySharedParametersCombinedReport_single.csv": (
                    True,
                    1,
                    [self.single_family_shared_parameters_01],
                ),
                "FamilyWarningsCombinedReport_single.csv": (True, 1, []),
            }

            for test_file, test_result in test_files.items():
                return_value.append_message(
                    "\n" + "Reading test file: [{}]".format(test_file)
                )
                try:
                    # read overall family data
                    family_base_data_result = read_data_into_family_containers(
                        os.path.join(TEST_REPORT_DIRECTORY, test_file)
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

                return_value.append_message(
                    "...expecting status: {} and got: {}".format(
                        test_result[0], family_base_data_result.status
                    )
                )
                assert family_base_data_result.status == test_result[0]
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
            # flag = False
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {} : {}".format(self.test_name, e),
            )
        return return_value.status, return_value.message
