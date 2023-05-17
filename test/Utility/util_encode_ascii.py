"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains utility encode ascii string tests . 
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
    encode_ascii,
)


class EncodeASCII(test.Test):
    def __init__(self):
        # store document in base class
        super(EncodeASCII, self).__init__(
            test_name="encode string as ascii"
        )

    def test(self):
        """
        encode_ascii test

        :return: True if all tests past, otherwise False. A message containing results.
        :rtype: bool, str
        """

        flag = True
        message = "-"
        try:
            result = encode_ascii("hello world")
            message = "{} \nvs \n{}".format(result, b"hello world")
            assert encode_ascii(result) == b"hello world"

            result = encode_ascii("Привет, мир!")
            message = message + "\n" + (" {} vs {}".format(result, b"?, ?!"))
            assert encode_ascii(result) == b"??????, ???!"

            result = encode_ascii("")
            message = message + "\n" + (" {} vs {}".format(result, b""))
            assert encode_ascii("") == b""

            result = encode_ascii("123")
            message = message + "\n" + (" {} vs {}".format(result, b"123"))
            assert encode_ascii("123") == b"123"

            result = encode_ascii(123)
            message = message + "\n" + (" {} vs {}".format(result, 123))
            assert encode_ascii(123) == 123

            result = encode_ascii(None)
            message = message + "\n" + (" {} vs {}".format(result, None))
            assert encode_ascii(None) == None

            result = encode_ascii(True)
            message = message + "\n" + (" {} vs {}".format(result, True))
            assert encode_ascii(True) == True

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
