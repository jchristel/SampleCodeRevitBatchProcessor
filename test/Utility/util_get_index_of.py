"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains get index of item in list tests . 
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

from duHast.Utilities.utility import (
    index_of,
)


class GetIndexOf(test.Test):
    def __init__(self):
        # store document in base class
        super(GetIndexOf, self).__init__(test_name="get index of item in list")

    def test(self):
        """
        index of test

        :return: True if all tests past, otherwise False. A message containing results.
        :rtype: bool, str
        """

        flag = True
        message = "-"
        try:
            # Test with a list that contains the item
            result = index_of([1, 2, 3, 4], 3)
            message = "{} \nvs \n{}".format(result, 2)
            assert index_of([1, 2, 3, 4], 3) == 2

            # Test with a list that doesn't contain the item
            result = index_of([1, 2, 3, 4], 5)
            message = message + "\n" + (" {} vs {}".format(result, -1))
            assert index_of([1, 2, 3, 4], 5) == -1

            # Test with an empty list
            result = index_of([], 1)
            message = message + "\n" + (" {} vs {}".format(result, -1))
            assert index_of([], 1) == -1

            # Test with a list of strings
            result = index_of(["apple", "banana", "orange"], "banana")
            message = message + "\n" + (" {} vs {}".format(result, 1))
            assert index_of(["apple", "banana", "orange"], "banana") == 1

            # Test with a list of mixed types
            result = index_of([1, "apple", 2, "banana"], "banana")
            message = message + "\n" + (" {} vs {}".format(result, 3))
            assert index_of([1, "apple", 2, "banana"], "banana") == 3

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
