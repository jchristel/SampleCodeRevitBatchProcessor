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
