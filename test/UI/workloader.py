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
from collections import namedtuple
from test.utils import test

from duHast.UI.workloader import distribute_workload
from duHast.UI.file_item import MyFileItem
from duHast.UI.file_list import get_file_size
import uuid

TEST_RESULT = namedtuple(
    "test_result", "test_id bucket_size all_items items_per_bucket"
)


class Workloader(test.Test):
    def __init__(self):
        # store document in base class
        super(Workloader, self).__init__(test_name="workloader")

    def _check_items_per_bucket(self, buckets, test_outcome):
        """
        Checks that items per bucket count and the actual items are as expected.

        :param buckets: A workload_bucket object
        :type buckets: WorkloadBucket
        :param test_outcome: A tuple containing the test outcome values
        :type test_outcome: namedtuple
        :return: A boolean (True if all tests past, otherwise False), a message containing test data
        :rtype: bool, str
        """

        flag = True
        bucket_counter = 0
        message = ""
        for bucket in buckets:
            try:
                # check number of items per bucket
                message = (
                    message
                    + "\n bucket items count: item count: \nexpected: {} \nvs: {}".format(
                        len(test_outcome.items_per_bucket[bucket_counter]),
                        len(bucket.items),
                    )
                )
                assert len(test_outcome.items_per_bucket[bucket_counter]) == len(
                    bucket.items
                )
                # check items per bucket
                message = message + "\n bucket items : item : \nexpected: {} \nvs: {}".format(
                    # sort both item list by name
                    sorted(
                        test_outcome.items_per_bucket[bucket_counter],
                        key=lambda obj: obj.name,
                    ),
                    sorted(bucket.items, key=lambda obj: obj.name),
                )
                assert sorted(
                    # sort both item list by name
                    test_outcome.items_per_bucket[bucket_counter],
                    key=lambda obj: obj.name,
                ) == sorted(bucket.items, key=lambda obj: obj.name)
            except Exception as e:
                flag = False
                message = (
                    message
                    + "\n"
                    + (
                        "An exception occurred in function (check_items_per_bucket) {} : {}".format(
                            self.test_name, e
                        )
                    )
                )
            bucket_counter = bucket_counter + 1
        return flag, message

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

            # these should be the test results
            test_outcome = [
                # single bucket test with 2 files
                TEST_RESULT(
                    test_id=0,
                    bucket_size=1,
                    all_items=test_files,
                    items_per_bucket=[test_files],
                ),
                # 2 buckets test with 2 files
                TEST_RESULT(
                    test_id=1,
                    bucket_size=2,
                    all_items=test_files,
                    items_per_bucket=[[test_files[0]], [test_files[1]]],
                ),
                # 3 buckets test with 2 files
                TEST_RESULT(
                    test_id=2,
                    bucket_size=3,
                    all_items=test_files,
                    items_per_bucket=[[test_files[0]], [test_files[1]], []],
                ),
            ]

            for test in test_outcome:
                # distribute files into buckets
                result = distribute_workload(
                    test.bucket_size, test.all_items, get_file_size
                )
                # record bucket size outcome
                message = message + "\n bucket size : expected: {} vs: {}".format(
                    test.bucket_size, len(result)
                )
                # test bucket size outcome
                assert len(result) == test.bucket_size
                # check contents of bucket(s)
                (
                    flag_bucket_content,
                    message_bucket_content,
                ) = self._check_items_per_bucket(buckets=result, test_outcome=test)
                flag = flag & flag_bucket_content
                message = "{}\n{}".format(message, message_bucket_content)

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
