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
from test.utils import test

from duHast.Utilities.files_io import get_directory_path_from_file_path
from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.Data.family_report_reader import read_data_into_families

TEST_REPORT_DIRECTORY_MULTIPLE = os.path.join(
    get_directory_path_from_file_path(__file__), "ReadFamilies_01"
)


class DataCullingNestedFamilies(test.Test):

    def __init__(self):
        # store document in base class
        super(DataCullingNestedFamilies, self).__init__(
            test_name="data_culling_nested_families"
        )

    def _run_tests(self, test_data, test_files_directory):
        """
        actual test runner
        """
        return_value = Result()
        #return_value.append_message("\n{}\n".format(test_data))
        # test reports
        try:
            # run tests
            test_result_multiple = read_data_into_families(test_files_directory)
            return_value.update(test_result_multiple)
            return_value.append_message(
                "Number of family instances: {} vs expected: {}".format(
                    len(test_result_multiple.result), len(test_data)
                )
            )
            # expecting 14 family instances
            assert len(test_result_multiple.result) == len(test_data)

            return_value.append_message("Processing families...")
            # process all families before checking longest path
            for family_instance in test_result_multiple.result:
                try:
                    family_instance.process()
                except Exception as e:
                    return_value.update_sep(
                        False,
                        "An exception occurred in function process family : {}".format(
                            e
                        ),
                    )

            # check if all families are accounted for and have the right number of containers loaded
            for family_name, unique_longest_path_from_test_data in test_data.items():
                found_match = False
                for family_instance in test_result_multiple.result:
                    if family_instance.family_name == family_name:
                        found_match = True
                        return_value.append_message(
                            "Family {} found in loaded family instances".format(
                                family_name
                            )
                        )

                        unique_longest_path_from_family = (
                            family_instance.get_longest_unique_nesting_path()
                        )
                        return_value.append_message(
                            "Longest unique path found {}: vs expected: {}".format(
                                len(unique_longest_path_from_family),
                                unique_longest_path_from_test_data[0],
                            )
                        )

                        try:
                            assert (
                                len(unique_longest_path_from_family)
                                == unique_longest_path_from_test_data[0]
                            )
                        except Exception as e:
                            return_value.update_sep(
                                False, "Longest unique path found \n...{}".format("\n...".join(unique_longest_path_from_family)))

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
                "An exception: {} occurred in function _test runner : {}".format(e, self.test_name),
            )

        return return_value

    def test(self):
        """
        Culls nested family data by removing all nested families from the data set but the longest uniques root path.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        return_value = Result()

        try:

            # test multiple families per report
            # 4 test files
            test_files_multiple = {
                "Sample_Family_One": (2,),
                "Sample_Family_Two": (2,),
                "Sample_Family_Three": (1,),
                "Sample_Family_Four": (1,),
                "Sample_Family_Five": (1,),
                "Sample_Family_Six": (5,),
                "Sample_Family_Seven": (3,),
                "Sample_Family_Eight": (1,),
                "Sample_Family_Nine": (2,),
                "Sample_Family_Ten": (1,),
                "Sample_Family_Eleven": (1,),
                "Sample_Family_Twelve": (1,),
                "Sample_Family_Thirteen": (1,),
                "Sample_Family_Fourteen": (1,),
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
