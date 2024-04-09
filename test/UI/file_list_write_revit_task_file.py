"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains write_revit_task_file tests . 
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
from collections import namedtuple
import uuid
from test.utils import test


from duHast.UI.workloader import distribute_workload
from duHast.UI.Objects.file_item import MyFileItem
from duHast.UI.file_list import (
    get_file_size,
    write_revit_task_file,
    bucket_to_task_list_file_system,
    bucket_to_task_list_bim_360,
)
from duHast.Utilities.files_io import file_exist
from duHast.Utilities.files_csv import read_csv_file


TEST_RESULT = namedtuple(
    "test_result",
    "test_id bucket_size all_items items_per_bucket bucket_get_data task_file_names",
)


class WriteRevitTaskFile(test.Test):
    def __init__(self):
        # store document in base class
        super(WriteRevitTaskFile, self).__init__(test_name="write_revit_task_file")

    def _check_items_per_task_file(
        self, temp_dir, task_file_name, task_file_content, task_file_content_converter
    ):
        flag = True
        
        message = ""
        try:
            # read task file as csv file
            data = read_csv_file(os.path.join(temp_dir, task_file_name))
            # compare content with expected content
            expected_content = []
            for raw in task_file_content:
                # results are reads as a list per row!
                expected_content.append([task_file_content_converter(raw)])

            # check items per file
            message = message + "\n file items : item : \nexpected: {} \nvs: {}".format(
                # sort both item list
                sorted(expected_content),
                sorted(data),
            )
            assert sorted(expected_content) == sorted(data)

        except Exception as e:
            flag = False
            message = (
                message
                + "\n"
                + (
                    "An exception occurred in function (check_items_per_task_file) {} : {}".format(
                        self.test_name, e
                    )
                )
            )
        
        return flag, message

    def test(self):
        """
        Test write_revit_task_file.

        :return: True if all tests past, otherwise False
        :rtype: bool
        """

        flag = True
        message = "-"
        try:
            # test data for BIM 360 files
            test_files_BIM_360 = [
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

            # test data for BIM 360 files
            test_files_file_server = [
                MyFileItem(
                    "test_file_01_size.rvt",
                    100,
                ),
                MyFileItem(
                    "test_file_02_size.rvt",
                    50,
                ),
            ]

            # these should be the test results
            test_outcome = [
                # single bucket test with 2 files
                TEST_RESULT(
                    test_id=0,
                    bucket_size=1,
                    all_items=test_files_BIM_360,
                    items_per_bucket=[test_files_BIM_360],
                    bucket_get_data=bucket_to_task_list_bim_360,
                    task_file_names=["task_file.csv"],
                ),
                # 2 buckets test with 2 files
                TEST_RESULT(
                    test_id=1,
                    bucket_size=2,
                    all_items=test_files_BIM_360,
                    items_per_bucket=[[test_files_BIM_360[0]], [test_files_BIM_360[1]]],
                    bucket_get_data=bucket_to_task_list_bim_360,
                    task_file_names=["task_file_1.csv", "task_file_2.csv"],
                ),
                # 3 buckets test with 2 files
                TEST_RESULT(
                    test_id=2,
                    bucket_size=3,
                    all_items=test_files_BIM_360,
                    items_per_bucket=[
                        [test_files_BIM_360[0]],
                        [test_files_BIM_360[1]],
                        [],
                    ],
                    bucket_get_data=bucket_to_task_list_bim_360,
                    task_file_names=[
                        "task_file_1.csv",
                        "task_file_2.csv",
                        "task_file_3.csv",
                    ],
                ),
                # single bucket test with 2 files
                TEST_RESULT(
                    test_id=3,
                    bucket_size=1,
                    all_items=test_files_file_server,
                    items_per_bucket=[test_files_file_server],
                    bucket_get_data=bucket_to_task_list_file_system,
                    task_file_names=["task_file.csv"],
                ),
                # 2 buckets test with 2 files
                TEST_RESULT(
                    test_id=4,
                    bucket_size=2,
                    all_items=test_files_file_server,
                    items_per_bucket=[
                        [test_files_file_server[0]],
                        [test_files_file_server[1]],
                    ],
                    bucket_get_data=bucket_to_task_list_file_system,
                    task_file_names=["task_file_1.csv", "task_file_2.csv"],
                ),
                # 3 buckets test with 2 files
                TEST_RESULT(
                    test_id=5,
                    bucket_size=3,
                    all_items=test_files_file_server,
                    items_per_bucket=[
                        [test_files_file_server[0]],
                        [test_files_file_server[1]],
                        [],
                    ],
                    bucket_get_data=bucket_to_task_list_file_system,
                    task_file_names=[
                        "task_file_1.csv",
                        "task_file_2.csv",
                        "task_file_3.csv",
                    ],
                ),
            ]

            for test in test_outcome:
                # distribute files into buckets
                buckets = distribute_workload(
                    test.bucket_size, test.all_items, get_file_size
                )
                # record bucket size outcome
                message = message + "\n bucket size : expected: {} vs: {}".format(
                    test.bucket_size, len(buckets)
                )
                # test bucket size outcome
                assert len(buckets) == test.bucket_size
                # write out data into temp directory
                def action(tmp_dir):
                    # attempt to write data to file
                    bucket_counter = 0
                    for bucket in buckets:
                        flag_action = True
                        message_action = ""
                        # write out task file for bucket
                        write_result = write_revit_task_file(
                            file_name=os.path.join(
                                tmp_dir, test.task_file_names[bucket_counter]
                            ),
                            bucket=bucket,
                            get_data=test.bucket_get_data,
                        )
                        # check if task file was written ok
                        flag_action = flag_action & write_result.status
                        message_action = message_action + "\n" + write_result.message
                        assert write_result.status == True
                        # check file really exists
                        file_exist_flag = file_exist(
                            os.path.join(tmp_dir, test.task_file_names[bucket_counter])
                        )
                        message_action = "{}\nfile exists expected: {} vs: {}".format(
                            message_action, True, file_exist_flag
                        )

                        assert file_exist_flag == True
                        # check file content
                        (
                            flag_task_file_content,
                            message_task_file_content,
                        ) = self._check_items_per_task_file(
                            task_file_name=test.task_file_names[bucket_counter],
                            temp_dir=tmp_dir,
                            task_file_content=test.items_per_bucket[bucket_counter],
                            task_file_content_converter=test.bucket_get_data,
                        )
                        # combine status and messages
                        flag_action = flag_action & flag_task_file_content
                        message_action = "{}\n{}".format(
                            message_action, message_task_file_content
                        )
                        bucket_counter = bucket_counter + 1
                    return flag_action, message_action

                flag_check, message_check = self.call_with_temp_directory(action)
                flag = flag & flag_check
                message = message + "\n" + message_check
                
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
