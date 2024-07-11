"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains data find missing root families direct hosts tests. 
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
from test.utils import test

from duHast.Utilities.files_io import get_directory_path_from_file_path
from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.Data.family_base_data_missing_families import (
    find_missing_families_direct_host_families,
)

TEST_REPORT_DIRECTORY_MULTIPLE = os.path.join(
    get_directory_path_from_file_path(__file__), "ReadMissingFamilies_01"
)


class DataMissingFamiliesDirectHostFamilies(test.Test):

    def __init__(self):
        # store document in base class
        super(DataMissingFamiliesDirectHostFamilies, self).__init__(
            test_name="data_missing_families_direct_hosts"
        )

    def _run_tests(self, test_data, test_files_directory):
        """
        actual test runner
        """
        return_value = Result()
        # return_value.append_message("\n{}\n".format(test_data))

        # test reports
        try:
            # run tests
            test_result_missing_hosts = find_missing_families_direct_host_families(
                test_files_directory
            )
            return_value.update(test_result_missing_hosts)
            return_value.append_message(
                "Number of missing families hosts: {} vs expected: {}".format(
                    len(test_result_missing_hosts.result), len(test_data)
                )
            )
            # expecting 1 family instances
            assert len(test_result_missing_hosts.result) == len(test_data)

            # check if missing family hosts where identified correctly
            for family_data in test_data:
                if family_data in test_result_missing_hosts.result:
                    return_value.append_message(
                        "Test family {} found in result data".format(family_data)
                    )
                else:
                    return_value.append_message(
                        "Test family {} not found in result data".format(family_data)
                    )

                try:
                    assert family_data in test_result_missing_hosts.result

                except Exception as e:
                    return_value.update_sep(
                        False,
                        "Missing root family from test data not found in result...",
                    )

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function _test runner : {}".format(
                    self.test_name, e
                ),
            )

        return return_value

    def test(self):
        """
        Checks library for missing families and returns their direct host families.
        A missing family is a family which appears as a nested family only but never as a root family.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        return_value = Result()

        try:

            # test families for missing families
            # should be one...
            test_files_multiple = [
                ("Sample_Family_Six", "Specialty Equipment"),
                ("Sample_Family_Nine", "Furniture Systems"),
                ("Sample_Family_Two", "Furniture Systems"),
            ]

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
