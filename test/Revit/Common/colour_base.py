"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains colour base tests . 
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

from test.Revit.TestUtils import revit_test
from duHast.Revit.Common.Objects.Data.colour_base import ColourBase
from duHast.Utilities.Objects import result as res

# import Autodesk
import Autodesk.Revit.DB as rdb


class ColourB(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(ColourB, self).__init__(doc=doc, test_name="colour base tests")

    def test(self):
        """
        colour base tests

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .status True if colour base tests completed successfully, otherwise False.
                - .message will contain result(s) vs expected result(s)
                - . result (empty list)

                on exception:

                - .result Will be False
                - .message will contain exception message.
                - . result (empty list)
        :rtype: :class:`.Result`
        """

        return_value = res.Result()

        try:
            data_set = {
                1: {"red": 100, "green": 100, "blue": 100},
                2: {"red": 90, "green": 100, "blue": 100},
                3: {"red": 100, "green": 90, "blue": 100},
                4: {"red": 100, "green": 100, "blue": 90},
            }

            # test class initialization
            for k, v in data_set.items():
                test_colour = ColourBase(v)
                return_value.append_message(
                    " {} vs {}".format(test_colour.to_json(), v)
                )
                # check values
                # vars(object instance) returns a dictionary of the class instance properties
                assert vars(test_colour) == v

            data_set = {
                1: {
                    "first": {"red": 100, "green": 100, "blue": 100},
                    "second": {"red": 100, "green": 100, "blue": 100},
                    "is_equal": True,
                },
                2: {
                    "first": {"red": 100, "green": 100, "blue": 0},
                    "second": {"red": 100, "green": 100, "blue": 100},
                    "is_equal": False,
                },
                3: {
                    "first": {"red": 100, "green": 0, "blue": 100},
                    "second": {"red": 100, "green": 100, "blue": 100},
                    "is_equal": False,
                },
                4: {
                    "first": {"red": 0, "green": 100, "blue": 100},
                    "second": {"red": 100, "green": 100, "blue": 100},
                    "is_equal": False,
                },
            }

            # test class instance comparison
            for k, v in data_set.items():
                test_colour_one = ColourBase(v["first"])
                test_colour_two = ColourBase(v["second"])
                return_value.append_message(
                    " {} vs {} is equal: {}".format(
                        test_colour_one.to_json(),
                        test_colour_two.to_json(),
                        v["is_equal"],
                    )
                )
                is_equal = test_colour_one == test_colour_two
                assert is_equal == v["is_equal"]

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )

        return return_value
