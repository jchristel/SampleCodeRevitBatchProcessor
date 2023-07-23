"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains remove items from list tests . 
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
    remove_items_from_list,
)


class RemoveItemsFromList(test.Test):
    def __init__(self):
        # store document in base class
        super(RemoveItemsFromList, self).__init__(test_name="remove items from list")

    def test(self):
        """
        remove_items test

        :return: True if all tests past, otherwise False. A message containing results.
        :rtype: bool, str
        """

        flag = True
        message = "-"
        try:
            # Test removing items from a list
            source_list = [1, 2, 3, 4, 5]
            remove_list = [2, 4]
            expected_result = [1, 3, 5]
            result = remove_items_from_list(source_list, remove_list)
            message = "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            # remove non existing items
            source_list = [1, 2, 3, 4, 5]
            remove_list = [6, 7]
            expected_result = [1, 2, 3, 4, 5]
            result = remove_items_from_list(source_list, remove_list)
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            # test empty lists
            source_list = []
            remove_list = []
            expected_result = []
            result = remove_items_from_list(source_list, remove_list)
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

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
