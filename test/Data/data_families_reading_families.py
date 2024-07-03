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

from test.utils import test

from duHast.Utilities.files_io import get_directory_path_from_file_path
from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.Data.family_report_reader import read_data_into_families

TEST_REPORT_DIRECTORY_MULTIPLE = os.path.join(
    get_directory_path_from_file_path(__file__), "ReadFamilies_01"
)


class DataReadFamiliesIntoFamilyInstances(test.Test):

    def __init__(self):
        # store document in base class
        super(DataReadFamiliesIntoFamilyInstances, self).__init__(
            test_name="read multiple family data into multiple family instances"
        )

    def _run_tests(self, test_data, test_files_directory):
        """
        actual test runner
        """
        return_value = Result()
        # test reports
        try:
            # run tests
            test_result_multiple = read_data_into_families(
                TEST_REPORT_DIRECTORY_MULTIPLE
            )
            return_value.update(test_result_multiple)
            return_value.append_message(
                "Number of family instances: {} vs expected: {}".format(
                    len(test_result_multiple.result), len(test_data)
                )
            )
            # expecting 14 family instances
            assert len(test_result_multiple.result) == len(test_data)

            # check if all families are accounted for and have the right number of containers loaded
            for family_name, expected_number_of_containers in test_data.items():
                found_match = False
                for family_instance in test_result_multiple.result:
                    if family_instance.family_name == family_name:
                        found_match = True
                        return_value.append_message(
                            "Family {} found in loaded family instances".format(
                                family_name
                            )
                        )
                        return_value.append_message(
                            "Family {} has {} containers loaded. Expected: {}".format(
                                family_name,
                                len(family_instance.data_containers_unsorted),
                                expected_number_of_containers[0],
                            )
                        )
                        assert (
                            len(family_instance.data_containers_unsorted)
                            == expected_number_of_containers[0]
                        )
                        break
                if not found_match:
                    return_value.update_sep(
                        False,
                        "Family {} not found in loaded family instances".format(
                            family_name
                        ),
                    )
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {} : {}".format(self.test_name, e),
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
                "Sample_Family_One": (4,),
                "Sample_Family_Two": (4,),
                "Sample_Family_Three": (2,),
                "Sample_Family_Four": (2,),
                "Sample_Family_Five": (2,),
                "Sample_Family_Six": (9,),
                "Sample_Family_Seven": (5,),
                "Sample_Family_Eight": (2,),
                "Sample_Family_Nine": (4,),
                "Sample_Family_Ten": (1,),
                "Sample_Family_Eleven": (2,),
                "Sample_Family_Twelve": (1,),
                "Sample_Family_Thirteen": (1,),
                "Sample_Family_Fourteen": (2,),
            }

            # make sure all families are accounted for and got the right number of containers loaded
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
