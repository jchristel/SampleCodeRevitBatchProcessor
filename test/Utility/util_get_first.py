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
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of Jan Christel nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by Jan Christel "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall Jan Christel be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
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
