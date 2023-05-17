"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains directory date stamp tests . 
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
from datetime import datetime

from duHast.Utilities.date_stamps import get_file_date_stamp, get_date_stamped_file_name


class GetDateStampFile(test.Test):
    def __init__(self):
        # store document in base class
        super(GetDateStampFile, self).__init__(test_name = "get_file_date_stamp")

    def test(self):
        """
        get_date_stamped_file_name() test

        :return: True if all tests pass, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "-"
        try:
            revit_file_path = "C:/Users/User/Documents/RevitFile.rvt"
            file_extension = ".txt"
            file_suffix = "_backup"

            date_stamp = get_file_date_stamp()
            result = date_stamp + "_RevitFile_backup.txt"

            # Call the function to get the actual output
            expected_result = get_date_stamped_file_name(
                revit_file_path, file_extension, file_suffix
            )
            message = " {} vs {}".format(result, expected_result)

            # Assert the actual output matches the expected output
            assert expected_result == result
        except Exception as e:
            print(
                "An exception occurred in function test_get_date_stamped_file_name {}".format(
                    e
                )
            )
            flag = False
        return flag, message
