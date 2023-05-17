"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains csv read file tests . 
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

from duHast.Utilities.files_csv import (
    read_csv_file,
)


class FileCSVRead(test.Test):
    def __init__(self):
        # store document in base class
        super(FileCSVRead, self).__init__(test_name="read_csv_file")

    def test(self):
        """
        read csv file test

        :param tmp_dir: temp directory
        :type tmp_dir: str
        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "-"
        try:
            # test data
            data = [
                "1,John,Doe",
                "2,Jane,Smith",
                "3,Bob,Johnson",
            ]

            data_long = [
                "1,John,Doe," + "1234567890" * 1000,
                "2,Jane,Smith," + "0987654321" * 1000,
                "3,Bob,Johnson," + "5555555555" * 1000,
            ]

            csv_file = "test_file.csv"

            # test short data
            def action_one(tmp_dir):
                flag_action = True
                message_action = ""
                try:
                    # write test file
                    self.write_file_with_data(csv_file, tmp_dir, data)

                    # Test reading the CSV file
                    result = read_csv_file(os.path.join(tmp_dir, csv_file))
                    expected_result = [
                        ["1", "John", "Doe"],
                        ["2", "Jane", "Smith"],
                        ["3", "Bob", "Johnson"],
                    ]
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

            # test long data
            def action_two(tmp_dir):
                flag_action = True
                message_action = ""
                try:
                    # test read csv file with large field size limit
                    # write test file
                    self.write_file_with_data(csv_file, tmp_dir, data_long)

                    result = read_csv_file(os.path.join(tmp_dir, csv_file))
                    expected_result = [
                        ["1", "John", "Doe", "1234567890" * 1000],
                        ["2", "Jane", "Smith", "0987654321" * 1000],
                        ["3", "Bob", "Johnson", "5555555555" * 1000],
                    ]
                    message_action = "{} \nvs \n{}".format(result, expected_result)
                    assert result == expected_result
                except Exception as e:
                    flag_action = False
                    message_action = (
                        message_action
                        + "\n"
                        + (
                            "An exception occurred in function {} data short: {}".format(
                                self.test_name,e
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
