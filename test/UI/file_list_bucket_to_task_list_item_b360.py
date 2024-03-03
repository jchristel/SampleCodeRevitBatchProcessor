"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains bucket_to_task_list_bim_360 tests . 
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

from duHast.UI.file_list import bucket_to_task_list_bim_360
from duHast.UI.Objects.file_item import MyFileItem
import uuid


class BucketToTaskListBIM360(test.Test):
    def __init__(self):
        # store document in base class
        super(BucketToTaskListBIM360, self).__init__(test_name="bucket_to_task_list_bim_360")

    def test(self):
        """
        Test bucket_to_task_list_bim_360.

        :return: True if all tests past, otherwise False
        :rtype: bool
        """

        flag = True
        message = "-"
        try:
            # test data
            test_files = [
                MyFileItem("test_file_01_size.rvt",100,uuid.uuid4(), uuid.uuid4(), uuid.uuid4()),
                MyFileItem("test_file_02_size.rvt",100,uuid.uuid4(), uuid.uuid4(), uuid.uuid4()),
            ]

            for file in test_files:
                result = bucket_to_task_list_bim_360(file)
                expected_result = ' '.join([file.bim_360_revit_version, file.bim_360_project_guid, file.bim_360_file_guid])
                message = "\n expected: {} vs: {}".format(
                    expected_result, result
                )
                assert result == expected_result

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
