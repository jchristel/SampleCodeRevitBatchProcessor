"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains file delete tests . 
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
    file_exist,
    file_delete,
)


class FileDelete(test.Test):
    def __init__(self):
        # store document in base class
        super(FileDelete, self).__init__(test_name="file_delete")

    def test(self):
        """
        file_delete test

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

            # test short data
            def action_one(tmp_dir):
                flag_action = True
                message_action = ""
                try:
                    self.write_test_files(test_files, tmp_dir)
                    result = file_delete(os.path.join(tmp_dir, test_files[0]))
                    expected_result = True
                    expected_result_check = file_exist(
                        os.path.join(tmp_dir, test_files[0])
                    )
                    message_action = (
                        "File deleted: {} vs  expected: {} vs file check {}".format(
                            result, expected_result, not expected_result_check
                        )
                    )
                    assert expected_result == result
                    # file exist should have returned a false!
                    assert result is not expected_result_check
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

            flag, message = self.call_with_temp_directory(action_one)

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
