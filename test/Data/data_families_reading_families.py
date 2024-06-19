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
                "": (True, 5, []),
                "FamilyBaseDataCombinedReport_multiple.csv": (
                    True,
                    5,
                    [],
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
                "FamilyWarningsCombinedReport_multiple.csv": (
                    True,
                    5,
                    [],
                ),
            }

            # run tests
            test_result_multiple = read_data_into_families(TEST_REPORT_DIRECTORY_MULTIPLE)
            return_value.update(test_result_multiple)
            # expecting 14 family instances
            assert len(test_result_multiple.result) == 14
        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {} : {}".format(self.test_name, e),
            )
        return return_value.status, return_value.message
