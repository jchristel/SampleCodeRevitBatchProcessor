"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains file name without extension tests . 
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
    get_file_name_without_ext,
)


class FileNameWithoutExtension(test.Test):
    def __init__(self):
        # store document in base class
        super(FileNameWithoutExtension, self).__init__(
            test_name="file_name_without_ext"
        )

    def test(self):
        """
        get_file_name_without_ext test

        :param tmpdir: temp directory
        :type tmpdir: str
        :return: True if all tests past, otherwise False. A message containing results.
        :rtype: bool, str
        """

        flag = True
        message = "-"
        try:
            file_path = "/path/to/example_file.txt"
            expected_result = "example_file"
            result = get_file_name_without_ext(file_path)
            message = " {} vs {}".format(result, expected_result)
            assert result == expected_result

            file_path = "/path/to/another_example_file.csv"
            expected_result = "another_example_file"
            result = get_file_name_without_ext(file_path)
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            file_path = "\\path/to/another_example_file.csv"
            expected_result = "another_example_file"
            result = get_file_name_without_ext(file_path)
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            file_path = "C:\path/to some/another_example_file.csv"
            expected_result = "another_example_file"
            result = get_file_name_without_ext(file_path)
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            file_path = "\\path/to/another_example_file.0001.csv"
            expected_result = "another_example_file.0001"
            result = get_file_name_without_ext(file_path)
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            file_path = "example_file.docx"
            expected_result = "example_file"
            result = get_file_name_without_ext(file_path)
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
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
