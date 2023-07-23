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
