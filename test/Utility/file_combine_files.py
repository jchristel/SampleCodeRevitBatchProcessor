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
                ["test_file_one.csv",["data 1","data 2","data 3"]], 
                ["test_file_two.csv",["data 4","data 4","data 5"]],
                ["test_file_three.csv",["data 1","data 2","data 3"]], 
            ]

            test_files_two = [
                ["test_file_one.csv",["data 1","data 3"]], 
                ["test_file_two.csv",["data 4","data 4","data 5"]],
                ["test_file_three.csv",["data 1","data 2"]],
                ["test_file_two.csv",["data 4","data 4","data 5","data 6"]],
            ]

            combined_file_name = 'result.csv'
            
            # test homogenous data
            def action_one(tmp_dir):
                flag_action = True
                message_action = ""
                try:
                    # write test files
                    for test_file in test_files:
                        self.write_file_with_data(test_file[0], tmp_dir, test_file[1])
                    # combine test files
                    result = combine_files(tmp_dir,"test",'','.csv',combined_file_name)
                    # reading the CSV file back in
                    result = read_csv_file(os.path.join(tmp_dir, combined_file_name))

                    # build expected result list
                    expected_result = [file[1][1] for file in test_files]
                    message_action = "{} \nvs \n{}".format(result, expected_result)
                    assert result == expected_result
                except Exception as e:
                    flag_action = False
                    message_action = (
                        message_action
                        + "\n"
                        + (
                            "An exception occurred in function {} data short: {}".format(
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
                        self.write_file_with_data(test_file[0], tmp_dir, test_file[1])
                    # combine test files
                    result = combine_files(tmp_dir,"test",'','.csv',combined_file_name)
                    # reading the CSV file back in
                    result = read_csv_file(os.path.join(tmp_dir, combined_file_name))

                    # build expected result list
                    expected_result = [file[1][1] for file in test_files_two]
                    message_action = "{} \nvs \n{}".format(result, expected_result)
                    assert result == expected_result
                except Exception as e:
                    flag_action = False
                    message_action = (
                        message_action
                        + "\n"
                        + (
                            "An exception occurred in function {} data short: {}".format(
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
                + ("An exception occurred in function {} : {}".format(self.test_name,e))
            )
        return flag, message
