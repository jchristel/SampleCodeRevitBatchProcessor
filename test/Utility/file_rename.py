"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains file rename tests . 
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
    rename_file,
)


class FileRename(test.Test):
    def __init__(self):
        # store document in base class
        super(FileRename, self).__init__(test_name="file_rename")

    def test(self):
        """
        Test file_exist.

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
                ["file.txt", "file_after.txt"],
                ["file_2.text", "file_after.txt"],
                ["file_2.text", ""],
            ]

            test_file_to_be_written = list(entry[0] for entry in test_files)

            # test short data
            def action_one(tmp_dir):
                flag_action = True
                message_action = ""
                try:
                    self.write_test_files(test_files,tmp_dir)
                    
                    # test valid scenario
                    result = rename_file(
                        os.path.join(tmp_dir, test_files[0][0]),
                        os.path.join(tmp_dir, test_files[0][1]),
                    )
                    result_file_exist = file_exist(os.path.join(tmp_dir, test_files[0][1]))
                    message_action = (
                        "rename result: {} vs expected result: {} vs file check result: {}".format(
                            result, True, result_file_exist
                        )
                    )
                    assert result == True
                    assert result == result_file_exist

                    result = rename_file(
                        os.path.join(tmp_dir, test_files[1][0]),
                        os.path.join(tmp_dir, test_files[1][1]),
                    )
                    message_action = message_action + "\n" + " {} vs {}".format(result, False)
                    assert result == False

                    result = rename_file(
                        os.path.join(tmp_dir, test_files[2][0]),
                        os.path.join(tmp_dir, test_files[2][1]),
                    )
                    message_action = message_action + "\n" + " {} vs {}".format(result, False)
                    assert result == False

                    # check non existing source file
                    result = rename_file(
                        os.path.join(tmp_dir, "not here.txt"),
                        os.path.join(tmp_dir, test_files[2][1]),
                    )
                    message_action = message_action + "\n" + " {} vs {}".format(result, False)
                    assert result == False

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
