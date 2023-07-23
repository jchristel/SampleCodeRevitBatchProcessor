"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains combine files tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

from test.utils import test
import os

from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.files_combine import (
    combine_files,
)


class FileCombineFiles(test.Test):
    def __init__(self):
        # store document in base class
        super(FileCombineFiles, self).__init__(test_name="combines_files")

    def test(self):
        """
        combine files test

        :param tmp_dir: temp directory
        :type tmp_dir: str
        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "-"
        try:
            # test data
            test_files = [
                [
                    "test_file_one.csv",
                    ["data 1", "data 2", "data 3"],
                    ["header 1", "header 2", "header 3"],
                ],
                [
                    "test_file_two.csv",
                    ["data 4", "data 4", "data 5"],
                    ["header 1", "header 2", "header 3"],
                ],
                [
                    "test_file_three.csv",
                    ["data 1", "data 2", "data 3"],
                    ["header 1", "header 2", "header 3"],
                ],
            ]

            test_files_two = [
                ["test_file_one.csv", ["data 1", "data 3"], ["header 1", "header 2"]],
                [
                    "test_file_two.csv",
                    ["data 4", "data 4", "data 5"],
                    ["header 1", "header 2", "header 3"],
                ],
                ["test_file_three.csv", ["data 1", "data 2"], ["header 1", "header 2"]],
                [
                    "test_file_four.csv",
                    ["data 4", "data 4", "data 5", "data 6"],
                    ["header 1", "header 2", "header 3", "header 4"],
                ],
            ]

            combined_file_name = "result.csv"

            # test homogenous data
            def action_one(tmp_dir):
                flag_action = True
                message_action = ""
                try:
                    # write test files
                    for test_file in test_files:
                        # set up header row
                        data = [",".join(test_file[2])]
                        # set up data row
                        data.append(",".join(test_file[1]))
                        self.write_file_with_data(test_file[0], tmp_dir, data)
                    # combine test files
                    result = combine_files(
                        tmp_dir, "test", "", ".csv", combined_file_name
                    )
                    # reading the CSV file back in
                    result = read_csv_file(os.path.join(tmp_dir, combined_file_name))
                    # build expected result list
                    expected_result = [file[1] for file in test_files]
                    # insert header row
                    expected_result.insert(0, test_files[0][2])
                    # compare lists sorted in case files got read in a different order when combined
                    message_action = "result: {} \nvs \nexpected: {}".format(
                        sorted(result), sorted(expected_result)
                    )
                    assert sorted(result) == sorted(expected_result)
                except Exception as e:
                    flag_action = False
                    message_action = (
                        message_action
                        + "\n"
                        + (
                            "An exception occurred in function {} uniform number of columns: {}".format(
                                self.test_name, e
                            )
                        )
                    )
                return flag_action, message_action

            # test non homogenous data
            def action_two(tmp_dir):
                flag_action = True
                message_action = ""
                try:
                    # write test files
                    for test_file in test_files_two:
                        # set up header row
                        data = [",".join(test_file[2])]
                        # set up data row
                        data.append(",".join(test_file[1]))
                        self.write_file_with_data(test_file[0], tmp_dir, data)
                    # combine test files
                    result = combine_files(
                        tmp_dir, "test", "", ".csv", combined_file_name
                    )
                    # reading the CSV file back in
                    result = read_csv_file(os.path.join(tmp_dir, combined_file_name))
                    # build expected result list
                    expected_result = [file[1] for file in test_files_two]
                    # insert first file header
                    expected_result.insert(0, test_files_two[0][2])
                    # compare lists sorted in case files got read in a different order when combined
                    message_action = "{} \nvs \n{}".format(
                        sorted(result), sorted(expected_result)
                    )
                    # should not be the same...
                    assert sorted(result) != sorted(expected_result)
                except Exception as e:
                    flag_action = False
                    message_action = (
                        message_action
                        + "\n"
                        + (
                            "An exception occurred in function {} varied number of columns: {}".format(
                                self.test_name, e
                            )
                        )
                    )
                return flag_action, message_action

            flag_one, message_one = self.call_with_temp_directory(action_one)
            flag_two, message_two = self.call_with_temp_directory(action_two)

            flag = flag_one & flag_two
            message = "{}\n{}".format(message_one, message_two)

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
