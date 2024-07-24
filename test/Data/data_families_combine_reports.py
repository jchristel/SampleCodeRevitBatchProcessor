"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains data combine reports tests . 
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
from duHast.Utilities.Objects.result import Result

from duHast.Revit.Family.Data.family_report_utils import combine_reports
from duHast.Utilities.files_io import get_directory_path_from_file_path


# test previous report empty and new report empty (01)
TEST_REPORT_DIRECTORY_ONE = os.path.join(
    get_directory_path_from_file_path(__file__), "CombineReports_01"
)

# test previous report empty but new report not empty (02)
TEST_REPORT_DIRECTORY_TWO = os.path.join(
    get_directory_path_from_file_path(__file__), "CombineReports_02"
)

# test previous report not empty but new report empty (03)
TEST_REPORT_DIRECTORY_THREE = os.path.join(
    get_directory_path_from_file_path(__file__), "CombineReports_03"
)

# test previous report not empty and new report not empty (04)
TEST_REPORT_DIRECTORY_FOUR = os.path.join(
    get_directory_path_from_file_path(__file__), "CombineReports_04"
)

# sub directories in test
PREVIOUS_REPORT_DIRECTORY_NAME = "previous"
NEW_REPORT_DIRECTORY_NAME = "new"


REPORTS_TO_COMBINE = {
    TEST_REPORT_DIRECTORY_ONE: [1,()],
    TEST_REPORT_DIRECTORY_TWO: [],
    TEST_REPORT_DIRECTORY_THREE: [],
    TEST_REPORT_DIRECTORY_FOUR: [],
}


class DataCombineFamiliesReports(test.Test):

    def __init__(self):
        # store document in base class
        super(DataCombineFamiliesReports, self).__init__(
            test_name="combine family data report"
        )

    def _run_tests(self, test_data, test_files_directory):
        """
        actual test runner
        """
        return_value = Result()
        # test reports
        try:
            # build directory names
            previous_directory = os.path.join(test_files_directory, PREVIOUS_REPORT_DIRECTORY_NAME)
            new_directory = os.path.join(test_files_directory, NEW_REPORT_DIRECTORY_NAME)

            # combine results
            combine_result = combine_reports(previous_report_path=previous_directory, new_report_path=new_directory)
            
            # check for exceptions
            if (combine_result.status == False):
                raise ValueError(combine_result.message)
            
            # test combine outcome
            # check number of families returned
            return_value.append_message ("expecting {} families in combined report. Got {}".format(test_data[0], len (combine_result.result)))

            # check if further tests required
            if(test_data[0]>0):
                pass
                # check family names and categories returned

                # check for specific value (file path ) indicating an update has ocurred

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function run tests : {}".format(e),
            )
        return return_value

    def test(self):
        """
        Combines family data report.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        return_value = Result()
        try:

            # loop over test directories, conduct test and compare outcome
            for directory, test_data in REPORTS_TO_COMBINE.items():
                test_result = self._run_tests(
                    test_data=test_data, test_files_directory=directory
                )
                return_value.update(test_result)

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {} : {}".format(self.test_name, e),
            )
        return return_value.status, return_value.message
