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
# BSD License
# Copyright © 2023, Jan Christel
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
