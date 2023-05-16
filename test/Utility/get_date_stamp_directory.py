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

from duHast.Utilities.date_stamps import get_folder_date_stamp


class GetDateStampDirectory(test.Test):
    def __init__(self):
        # store document in base class
        super(GetDateStampDirectory, self).__init__(test_name = "get_folder_date_stamp")

    def test(self):
        """
        _summary_

        :return: True if all tests pass, otherwise False
        :rtype: _bool
        """

        flag = True
        message = "-"
        try:
            # Test with default format
            expected_result = datetime.now().strftime("%Y%m%d")
            result = get_folder_date_stamp()
            message = " {} vs {}".format(result, expected_result)
            assert result == expected_result

            # Test with a different format
            expected_result = datetime.now().strftime("%Y-%m-%d")
            result = get_folder_date_stamp("%Y-%m-%d")
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            # Test with a invalid format
            expected_result = "invalid-format"
            result = get_folder_date_stamp("invalid-format")
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

        except Exception as e:
            message = (
                message
                + "\n"
                + (
                    "An exception occurred in function get_folder_date_stamp {}".format(
                        e
                    )
                )
            )
            flag = False
        return flag, message
