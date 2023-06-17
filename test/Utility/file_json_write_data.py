"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains json write data file tests . 
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

from duHast.Utilities.files_json import (
    write_json_to_file,
)


class FileJSONWriteData(test.Test):
    def __init__(self):
        # store document in base class
        super(FileJSONWriteData, self).__init__(test_name="write_json_to_file")

    def test(self):
        """
        write_json_to_file test

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
                {"Name": "John", "Age": 25, "Sex": "Male"},
                {"Name": "Sara", "Age": 32, "Sex": "Female"},
            ]

            json_file = "test_file.txt"

            # test short data
            def action_one(tmp_dir):
                flag_action = True
                message_action = ""
                # test file path
                full_json_path = os.path.join(tmp_dir, json_file)
                try:
                    # write test file
                    write_status = write_json_to_file(
                        json_data=data, data_output_file_path=full_json_path
                    )
                    message_action = write_status.message
                    flag_action = write_status.status

                    assert write_status.status == True

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
