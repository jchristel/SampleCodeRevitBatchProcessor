"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains workloader tests . 
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

from duHast.UI.workloader import distribute_workload
from duHast.UI.file_item import MyFileItem
from duHast.UI.file_list import get_file_size
import uuid


class Workloader(test.Test):
    def __init__(self):
        # store document in base class
        super(Workloader, self).__init__(test_name="workloader")

    def test(self):
        """
        Test workloader.

        :return: True if all tests past, otherwise False
        :rtype: bool
        """

        flag = True
        message = "-"
        try:
            # test data
            test_files = [
                MyFileItem(
                    "test_file_01_size.rvt",
                    100,
                    uuid.uuid4(),
                    uuid.uuid4(),
                    uuid.uuid4(),
                ),
                MyFileItem(
                    "test_file_02_size.rvt",
                    50,
                    uuid.uuid4(),
                    uuid.uuid4(),
                    uuid.uuid4(),
                ),
            ]

            # test a single bucket
            result = distribute_workload(1, test_files, get_file_size)
            message = "\n single bucket: expected: {} vs: {}".format(1, len(result))
            assert len(result) == 1
            # bucket should contain 2 items
            message = message + "\n single bucket: item count: expected: {} vs: {}".format(2, len(result[0].items))
            assert len(result[0].items) == 2

            for t_file in test_files:
                if t_file not in result[0].items:
                    message = message + "\n single bucket: items expected: {} not in bucket!".format(t_file)
                assert t_file in result[0].items

            # test 2 buckets
            result = distribute_workload(2, test_files, get_file_size)
            message = message + "\n two buckets: expected: {} vs: {}".format(2, len(result))
            assert len(result) == 2

            for test_bucket in result:
                # bucket should contain 1 items
                message = message + "\n two buckets: item count: expected: {} vs: {}".format(1, len(test_bucket.items))
                assert len(test_bucket.items) == 1


            # test 3 buckets
            result = distribute_workload(2, test_files, get_file_size)
            message = message + "\n three buckets: expected: {} vs: {}".format(3, len(result))
            assert len(result) == 3

            for test_bucket in result:
                # bucket should contain 1 items
                message = message + "\n three buckets: item count: expected: {} vs: {}".format(1, len(test_bucket.items))

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
