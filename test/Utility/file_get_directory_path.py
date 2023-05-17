"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains file directory path tests . 
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
    get_directory_path_from_file_path,
)


class FileGetDirectory(test.Test):
    def __init__(self):
        # store document in base class
        super(FileGetDirectory, self).__init__(test_name="file_get_directory")

    def test(self):
        """
        get_directory_path_from_file_path test

        :param tmpdir: temp directory
        :type tmpdir: str
        :return: True if all tests past, otherwise False. A message containing results.
        :rtype: bool, str
        """

        flag = True
        message = "-"
        try:
            # test data
            test_files = [
                ["/path/to/file.txt", "/path/to"],
                ["invalid/file/path", "invalid/file"],
                ["/path/to/directory/", "/path/to/directory"],
            ]

            # test valid file path
            result = get_directory_path_from_file_path(test_files[0][0])
            expected_result = test_files[0][1]
            message = " {} vs {}".format(result, expected_result)
            assert result == expected_result

            # test invalid file path
            result = get_directory_path_from_file_path(test_files[1][0])
            expected_result = test_files[1][1]
            message = message + "\n" + " {} vs {}".format(result, expected_result)
            assert result == expected_result

            # test directory path
            result = get_directory_path_from_file_path(test_files[2][0])
            expected_result = test_files[2][1]
            message = message + "\n" + " {} vs {}".format(result, expected_result)
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
