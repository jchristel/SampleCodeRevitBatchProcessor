"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility pad single digit numeric string tests . 
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
    pad_single_digit_numeric_string,
    PAD_SINGLE_DIGIT_TO_THREE,
)


class PadSingleDigitString(test.Test):
    def __init__(self):
        # store document in base class
        super(PadSingleDigitString, self).__init__(
            test_name="pad single digit numeric string"
        )

    def test(self):
        """
        pad_single_digit_numeric_string test

        :return: True if all tests past, otherwise False. A message containing results.
        :rtype: bool, str
        """

        flag = True
        message = "-"
        try:
            # Test padding a single digit integer string with two digits format
            result = pad_single_digit_numeric_string("5")
            message = "{} \nvs \n{}".format(result, "05")
            assert result == "05"

            result = pad_single_digit_numeric_string("8")
            message = message + "{} \nvs \n{}".format(result, "08")
            assert result == "08"

            result = pad_single_digit_numeric_string("9")
            message = message + "{} \nvs \n{}".format(result, "09")
            assert result == "09"

            # Test padding a single digit integer string with three digits format

            result = pad_single_digit_numeric_string(
                "5", format=PAD_SINGLE_DIGIT_TO_THREE
            )
            message = message + "{} \nvs \n{}".format(result, "005")
            assert result == "005"

            result = pad_single_digit_numeric_string(
                "8", format=PAD_SINGLE_DIGIT_TO_THREE
            )
            message = message + "{} \nvs \n{}".format(result, "008")
            assert result == "008"

            result = pad_single_digit_numeric_string(
                "9", format=PAD_SINGLE_DIGIT_TO_THREE
            )
            message = message + "{} \nvs \n{}".format(result, "009")
            assert result == "009"

            # Test with invalid input
            result = pad_single_digit_numeric_string("")
            message = message + "{} \nvs \n{}".format(result, "")
            assert result == ""

            result = pad_single_digit_numeric_string("not_a_digit")
            message = message + "{} \nvs \n{}".format(result, "not_a_digit")
            assert result == "not_a_digit"

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
