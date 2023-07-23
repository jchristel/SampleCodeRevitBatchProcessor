"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains csv write report file tests . 
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
import os, csv

from duHast.Utilities.files_csv import (
    write_report_data_as_csv,
)


class FileCSVWriteReport(test.Test):
    def __init__(self):
        # store document in base class
        super(FileCSVWriteReport, self).__init__(test_name="write_csv_report_file")

    def test(self):
        """
        write report data as csv test

        :param tmp_dir: temp directory
        :type tmp_dir: str
        :return: True if all tests past, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "-"
        try:
            # test data
            header = ["Name", "Age", "Gender"]
            data = [["John", "25", "Male"], ["Sara", "32", "Female"]]

            csv_file = "test_file.csv"

            # test short data
            def action_one(tmp_dir):
                flag_action = True
                message_action = ""
                # test file path
                full_csv_path = os.path.join(tmp_dir, csv_file)
                try:
                    # write test file
                    write_report_data_as_csv(full_csv_path, header, data)

                    with open(full_csv_path, "r") as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        message_action = "{} \nvs \n{}".format(rows[0], header)
                        message_action = (
                            message_action
                            + "\n"
                            + "{} \nvs \n{}".format(rows[1:], data)
                        )
                        assert rows[0] == header
                        assert rows[1:] == data

                    # Test appending to an existing file
                    more_data = [["Mike", "45", "Male"], ["Alice", "29", "Female"]]
                    write_report_data_as_csv(full_csv_path, [], more_data, "a")
                    with open(full_csv_path, "r") as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        message_action = (
                            message_action
                            + "\n"
                            + "{} \nvs \n{}".format(rows[0], header)
                        )
                        message_action = (
                            message_action
                            + "\n"
                            + "{} \nvs \n{}".format(rows[1:3], data)
                        )
                        message_action = (
                            message_action
                            + "\n"
                            + "{} \nvs \n{}".format(rows[3:], more_data)
                        )
                        assert rows[0] == header
                        assert rows[1:3] == data
                        assert rows[3:] == more_data

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
