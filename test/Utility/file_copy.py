"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains file copy tests . 
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

from duHast.Utilities.files_io import (
    copy_file,
    file_exist,
)


class FileCopy(test.Test):
    def __init__(self):
        # store document in base class
        super(FileCopy, self).__init__(test_name="file_copy")

    def test(self):
        """
        file_copy test

        :param tmpdir: temp directory
        :type tmpdir: str
        :return: True if all tests past, otherwise False
        :rtype: bool
        """

        flag = True
        message = "-"
        try:
            # test data
            test_files = [
                "test_file_size.txt",
            ]

            # test valid file copy
            def action_one(tmp_dir):
                flag_action = True
                message_action = ""
                new_file_name = os.path.join(tmp_dir,"new file_name.txt")
                try:
                    self.write_test_files(test_files, tmp_dir)
                    result = copy_file(os.path.join(tmp_dir, test_files[0]), new_file_name)
                    expected_result = True
                    expected_result_check = file_exist(new_file_name)
                    message_action = (
                        "File copy: {} vs  expected: {} vs file check {}".format(
                            result, expected_result, expected_result_check
                        )
                    )
                    assert expected_result == result
                    assert expected_result_check == result

                except Exception as e:
                    flag_action = False
                    message_action = (
                        message_action
                        + "\n"
                        + (
                            "An exception occurred in function  {} : {}".format(
                                self.test_name, e
                            )
                        )
                    )
                return flag_action, message_action
            
            # test in-valid file copy
            def action_two(tmp_dir):
                flag_action = True
                message_action = ""
                new_file_name = os.path.join(tmp_dir,"new file_name.txt")
                try:
                    self.write_test_files(test_files, tmp_dir)
                    result = copy_file("invalid/file/name.txt", new_file_name)
                    expected_result = False
                    expected_result_check = file_exist(new_file_name)
                    message_action = (
                        "File copy: {} vs  expected: {} vs file check {}".format(
                            result, expected_result, expected_result_check
                        )
                    )
                    assert expected_result == result
                    assert expected_result_check == result

                except Exception as e:
                    flag_action = False
                    message_action = (
                        message_action
                        + "\n"
                        + (
                            "An exception occurred in function  {} : {}".format(
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
