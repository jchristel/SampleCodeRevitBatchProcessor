"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains get_revit_files tests . 
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
import os

from test.utils import test

from duHast.UI.file_list import get_revit_files


class GetRevitFiles(test.Test):
    def __init__(self):
        # store document in base class
        super(GetRevitFiles, self).__init__(test_name="get_revit_files")

    def test(self):
        """
        Test get_revit_files.

        :return: True if all tests past, otherwise False
        :rtype: bool
        """

        flag = True
        message = "-"
        try:
            # test data
            test_files = [
                "test_file_size.rvt", # project file
                "test_file_size.0001.rvt", # back up file
            ]

            # test short data
            def action_one(tmp_dir):
                flag_action = True
                message_action = ""
                try:
                    self.write_test_files(test_files, tmp_dir)
                    result = get_revit_files(tmp_dir, ".rvt")
                    # should just get the project file back and not the back up file
                    expected_result = os.path.join(tmp_dir, test_files[0])
                    # returns a list of MyFileItem instances, match should be the first file!
                    message_action = " {} vs {}".format(result[0].name, expected_result)
                    assert expected_result == result[0].name
                    # only one item should have been returned
                    message_action = message_action + "\n {} vs {}".format(len(result), 1)
                    assert (len(result)) == 1
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
