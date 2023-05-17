"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility string to boolean tests . 
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
    parse_string_to_bool,
)


class StringToBool(test.Test):
    def __init__(self):
        # store document in base class
        super(StringToBool, self).__init__(test_name="parse string to bool")

    def test(self):
        """
        parse_string_to_bool test

        :return: True if all tests past, otherwise False. A message containing results.
        :rtype: bool, str
        """

        flag = True
        message = "-"
        try:
            result = parse_string_to_bool("true")
            message = "{} \nvs \n{}".format(result, True)
            assert result == True

            result = parse_string_to_bool("True")
            message = message + "{} \nvs \n{}".format(result, True)
            assert result == True

            result = parse_string_to_bool("false")
            message = message + "{} \nvs \n{}".format(result, False)
            assert result == False

            result = parse_string_to_bool("False")
            message = message + "{} \nvs \n{}".format(result, False)
            assert result == False

            try:
                result = parse_string_to_bool("abc")
                message = message + "{} \nvs \n{}".format(
                    result, "Expected exception not raised"
                )
                flag = False
                assert False, "Expected exception not raised"
            except Exception as e:
                assert str(e) == "String cant be converted to bool"

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
