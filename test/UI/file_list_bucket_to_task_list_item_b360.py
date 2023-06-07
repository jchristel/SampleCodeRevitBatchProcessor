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
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import os

from test.utils import test

from duHast.UI.file_list import bucket_to_task_list_bim_360
from duHast.UI.file_item import MyFileItem
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
