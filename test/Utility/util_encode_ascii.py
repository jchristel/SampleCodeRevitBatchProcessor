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
