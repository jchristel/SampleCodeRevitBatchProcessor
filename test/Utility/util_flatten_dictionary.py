"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains flatten dictionary tests . 
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
    flatten,
)


class FlattenDictionary(test.Test):
    def __init__(self):
        # store document in base class
        super(FlattenDictionary, self).__init__(test_name="flatten dictionary")

    def test(self):
        """
        flatten_dict test

        :return: True if all tests past, otherwise False. A message containing results.
        :rtype: bool, str
        """

        flag = True
        message = "-"
        try:
            # Test flattening a nested dictionary
            nested_dict = {
                "a": {"b": {"c": 1, "d": 2}},
                "e": {"f": {"g": 3, "h": 4}, "i": 5},
            }

            result = flatten(nested_dict)
            expected_result = {"a_b_c": 1, "a_b_d": 2, "e_f_g": 3, "e_f_h": 4, "e_i": 5}

            message = "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            # Test flattening an empty dictionary
            nested_dict = {}
            result = flatten(nested_dict)
            expected_result = {}
            message = message + "\n" + (" {} vs {}".format(result, expected_result))
            assert result == expected_result

            # Test flattening a dictionary with nested lists
            nested_dict = {"a": {"b": {"c": [1, 2, 3], "d": [4, 5]}}}
            result = flatten(nested_dict)
            expected_result = {"a_b_c": [1, 2, 3], "a_b_d": [4, 5]}
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
