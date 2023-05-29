"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains combine files tests of files with different headers per file. 
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

from test.utils import test
import os

from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.files_combine import (
    combine_files_csv_header_independent,
)


class FileCombineFilesIndependentHeadersCSV(test.Test):
    def __init__(self):
        # store document in base class
        super(FileCombineFilesIndependentHeadersCSV, self).__init__(test_name="combines_files_with_variant_headers_comma separator")

    def test(self):
        """
        combine comma separated files test with variant headers

        :param tmp_dir: temp directory
        :type tmp_dir: str
        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "-"
        try:
            test_file_extension = '.csv'
            
            # test data
            test_files = [
                [
                    "test_file_one",
                    ["data 1", "data 2", "data 3"],
                    ["header 1", "header 2", "header 3"],
                ],
                [
                    "test_file_two",
                    ["data 4", "data 4", "data 5"],
                    ["header 1", "header 2", "header 3"],
                ],
                [
                    "test_file_three",
                    ["data 1", "data 2", "data 3"],
                    ["header 1", "header 2", "header 3"],
                ],
            ]

            test_files_two = [
                ["test_file_four", ["data 1_header 1", "data 3_header 2"], ["header 1", "header 2"]],
                [
                    "test_file_five",
                    ["data 4_header 1", "data 4_header 3", "data 5_header 4"],
                    ["header 1", "header 3", "header 4"],
                ],
                ["test_file_six", ["data 1_header 4", "data 2_header 5"], ["header 4", "header 5"]],
                [
                    "test_file_seven",
                    ["data 4_header 1", "data 4_header 2", "data 5_header 3", "data 6_header 4"],
                    ["header 1", "header 2", "header 3", "header 4"],
                ],
            ]

            # test data
            test_files_three = [
                [
                    "test_file_eight",
                    ["data 1", "data 2", "data 3"],
                    ["header 1", "", "header 3"],
                ],
                [
                    "test_file_nine",
                    ["data 3", "data 4", "data 5"],
                    ["", "header 2", "header 3"],
                ],
                [
                    "test_file_ten",
                    ["data 1", "data 2", "data 3"],
                    ["header 1", "header 2", ""],
                ],
            ]

            combined_file_name_one = "result_one"+test_file_extension
            combined_file_name_two = "result_two"+test_file_extension
            combined_file_name_three = "result_three"+test_file_extension

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
                        self.write_file_with_data(test_file[0]+test_file_extension, tmp_dir, data)
                    # combine test files
                    result = combine_files_csv_header_independent(
                        tmp_dir, "test", "", test_file_extension, combined_file_name_one
                    )
                    # reading the tab separated file back in
                    result = read_csv_file(os.path.join(tmp_dir, combined_file_name_one))
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
                            "An exception occurred in function {} same headers: {}".format(
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
                        self.write_file_with_data(test_file[0]+test_file_extension, tmp_dir, data)
                    # combine test files
                    result = combine_files_csv_header_independent(
                        tmp_dir, "test", "", test_file_extension, combined_file_name_two
                    )
                    # reading the tab separated file back in
                    result = read_csv_file(os.path.join(tmp_dir, combined_file_name_two))
                    # build expected result list
                    expected_result = [
                        ["header 1","header 2","header 3","header 4","header 5"],
                        ["data 4_header 1","N/A","data 4_header 3","data 5_header 4","N/A"],
                        ["data 1_header 1","data 3_header 2","N/A","N/A","N/A"],
                        ["data 4_header 1","data 4_header 2","data 5_header 3","data 6_header 4",'N/A'],
                        ["N/A","N/A","N/A","data 1_header 4","data 2_header 5"],
                    ]
                    # compare lists sorted in case files got read in a different order when combined
                    message_action = "result: {} \nvs \nexpected: {}".format(
                        sorted(result), sorted(expected_result)
                    )
                    # should be the same...
                    assert sorted(result) == sorted(expected_result)
                except Exception as e:
                    flag_action = False
                    message_action = (
                        message_action
                        + "\n"
                        + (
                            "An exception occurred in function {} varied headers: {}".format(
                                self.test_name, e
                            )
                        )
                    )
                return flag_action, message_action

            # test non homogenous data with empty strings in header rows
            def action_three(tmp_dir):
                flag_action = True
                message_action = ""
                try:
                    # write test files
                    for test_file in test_files_three:
                        # set up header row
                        data = [",".join(test_file[2])]
                        # set up data row
                        data.append(",".join(test_file[1]))
                        self.write_file_with_data(test_file[0]+test_file_extension, tmp_dir, data)
                    # combine test files
                    result = combine_files_csv_header_independent(
                        tmp_dir, "test", "", test_file_extension, combined_file_name_three
                    )
                    # reading the tab separated file back in
                    result = read_csv_file(os.path.join(tmp_dir, combined_file_name_three))
                    # build expected result list
                    expected_result = [
                        ["header 1","header 2","header 3","test_file_eight.Empty.0","test_file_nine.Empty.0","test_file_ten.Empty.0"],
                        ["data 1","N/A","data 3","data 2","N/A","N/A"],
                        ["N/A","data 4","data 5","N/A","data 3","N/A"],
                        ["data 1","data 2","N/A","N/A","N/A","data 3"],
                    ]
                    # compare lists sorted in case files got read in a different order when combined
                    message_action = "result: {} \nvs \nexpected: {}".format(
                        sorted(result), sorted(expected_result)
                    )
                    # should be the same...
                    assert sorted(result) == sorted(expected_result)
                except Exception as e:
                    flag_action = False
                    message_action = (
                        message_action
                        + "\n"
                        + (
                            "An exception occurred in function {} varied headers with empty strings: {}".format(
                                self.test_name, e
                            )
                        )
                    )
                return flag_action, message_action
            
            flag_one, message_one = self.call_with_temp_directory(action_one)
            flag_two, message_two = self.call_with_temp_directory(action_two)
            flag_three, message_three = self.call_with_temp_directory(action_three)
            flag = flag_one & flag_two & flag_three
            message = "{}\n{}\n{}".format(message_one, message_two, message_three)

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
