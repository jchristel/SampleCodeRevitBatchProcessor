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
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
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
