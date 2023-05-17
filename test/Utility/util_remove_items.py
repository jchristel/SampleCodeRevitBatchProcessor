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
