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

from duHast.Revit.Family.Data.family_report_reader import (
    read_data_into_family_containers,
)
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

    def test(self):
        """
        Reads family data reports into container.

        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "\n-"
        try:

            # 4 test files
            test_files = {
                "": (True, 1, []),
                "FamilyBaseDataCombinedReport_single.csv": (True, 1, []),
                "FamilyCategoriesCombinedReport_single.csv": (True, 1, []),
                "FamilyLinePatternsCombinedReport_single.csv": (True, 1, []),
                "FamilySharedParametersCombinedReport_single.csv": (True, 1, []),
                "FamilyWarningsCombinedReport_single.csv": (True, 1, []),
            }

            for test_file, test_result in test_files.items():
                message = message + "\n" + "Reading test file: {}".format(test_file)
                # read overall family data
                family_base_data_result = read_data_into_family_containers(
                    os.path.join(TEST_REPORT_DIRECTORY, test_file)
                )
                message = message + "\n" + "..." + family_base_data_result.message

                message = (
                    message
                    + "\n"
                    + "...expecting status {} and got {}".format(
                        test_result[0], family_base_data_result.status
                    )
                )
                assert family_base_data_result.status == test_result[0]
                message = (
                    message
                    + "\n"
                    + "...expecting number of entries {} and got {}".format(
                        test_result[1], len(family_base_data_result.result)
                    )
                )
                assert len(family_base_data_result.result) == test_result[1]

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
