"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains get first item in list tests . 
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
    get_first,
)


class GetFirst(test.Test):
    def __init__(self):
        # store document in base class
        super(GetFirst, self).__init__(
            test_name="get first item in list"
        )

    def test(self):
        """
        get_first test

        :return: True if all tests past, otherwise False. A message containing results.
        :rtype: bool, str
        """

        flag = True
        message = "-"
        try:
            # Test when iterable is empty
            result = get_first([], None)
            message = "{} \nvs \n{}".format(result, None)
            assert get_first([], None) == None

            result = get_first([], "default")
            message = message + "\n" + (" {} vs {}".format(result, "default"))
            assert get_first([], "default") == "default"

            # Test when iterable is not empty and condition is met
            result = get_first([1, 2, 3], None, lambda x: x > 2)
            message = message + "\n" + (" {} vs {}".format(result, 3))
            assert get_first([1, 2, 3], None, lambda x: x > 2) == 3

            result = get_first([1, 2, 3], "default", lambda x: x > 2)
            message = message + "\n" + (" {} vs {}".format(result, 3))
            assert get_first([1, 2, 3], "default", lambda x: x > 2) == 3

            # Test when iterable is not empty but condition is not met
            result = get_first([1, 2, 3], None, lambda x: x > 5)
            message = message + "\n" + (" {} vs {}".format(result, None))
            assert get_first([1, 2, 3], None, lambda x: x > 5) == None

            result = get_first([1, 2, 3], "default", lambda x: x > 5)
            message = message + "\n" + (" {} vs {}".format(result, "default"))
            assert get_first([1, 2, 3], "default", lambda x: x > 5) == "default"

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
