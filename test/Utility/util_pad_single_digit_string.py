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
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
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
