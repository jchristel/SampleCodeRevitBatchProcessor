"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains line graphic base tests . 
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
from duHast.Revit.Common.Objects.Data.line_graphic_base import LineGraphicBase
from duHast.Utilities.Objects import result as res

# import Autodesk
# import Autodesk.Revit.DB as rdb


class LineGraphicB(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(LineGraphicB, self).__init__(doc=doc, test_name="line graphic base tests")

    def test(self):
        """
        line graphic base tests

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .status True if line graphic base tests completed successfully, otherwise False.
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
                1: {
                    "data_type": "test",
                    "colour": {"red": 100, "green": 100, "blue": 100},
                    "line_pattern_settings": {"name":"test_pattern", "id":1000},
                    "weight": 10,
                },
                2: {
                    "data_type": "test",
                    "colour": {"red": 10, "green": 100, "blue": 10},
                    "line_pattern_settings": {"name":"test_pattern", "id":1000},
                    "weight": 5,
                },
                3: {
                    "data_type": "test",
                    "colour": {"red": 50, "green": 50, "blue": 50},
                    "line_pattern_settings": {"name":"test_pattern", "id":1000},
                    "weight": 14,
                },
                4: {
                    "data_type": "test",
                    "colour": {"red": 100, "green": 10, "blue": 100},
                    "line_pattern_settings": {"name":"test_pattern", "id":1010},
                    "weight": 1,
                },
            }

            # test class initialization
            for k, v in data_set.items():
                test_line_graphic = LineGraphicBase(v["data_type"], v)
                return_value.append_message(
                    " {} vs {}".format(test_line_graphic.to_json(), v)
                )
                # check values
                assert test_line_graphic.class_to_dict() == v
            data_set = {
                1: {
                    "first": {
                        "data_type": "test",
                        "colour": {"red": 100, "green": 100, "blue": 100},
                        "line_pattern_settings": {"name":"test_pattern", "id":1000},
                        "weight": 10,
                    },
                    "second": {
                        "data_type": "test",
                        "colour": {"red": 100, "green": 100, "blue": 100},
                        "line_pattern_settings": {"name":"test_pattern", "id":1000},
                        "weight": 10,
                    },
                    "is_equal": True,
                },
                2: {
                    "first": {
                        "data_type": "test",
                        "colour": {"red": 100, "green": 100, "blue": 100},
                        "line_pattern_settings": {"name":"test_pattern", "id":1000},
                        "weight": 10,
                    },
                    "second": {
                        "data_type": "test",
                        "colour": {"red": 50, "green": 50, "blue": 50},
                        "line_pattern_settings": {"name":"test_pattern", "id":1000},
                        "weight": 14,
                    },
                    "is_equal": False,
                },
                3: {
                    "first": {
                        "data_type": "test",
                        "colour": {"red": 100, "green": 100, "blue": 100},
                        "line_pattern_settings": {"name":"test_pattern", "id":1000},
                        "weight": 10,
                    },
                    "second": {
                        "data_type": "test",
                        "colour": {"red": 100, "green": 100, "blue": 100},
                        "line_pattern_settings": {"name":"test_pattern_different", "id":1000},
                        "weight": 10,
                    },
                    "is_equal": False,
                },
            }

            # test class instance comparison
            for k, v in data_set.items():
                test_line_graphic_one = LineGraphicBase(
                    v["first"]["data_type"], v["first"]
                )
                test_line_graphic_two = LineGraphicBase(
                    v["second"]["data_type"], v["second"]
                )
                return_value.append_message(
                    " {} vs {} is equal: {}".format(
                        test_line_graphic_one.to_json(),
                        test_line_graphic_two.to_json(),
                        v["is_equal"],
                    )
                )
                is_equal = test_line_graphic_one == test_line_graphic_two
                assert is_equal == v["is_equal"]

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(
                    "test_line_graphic_base", e
                ),
            )

        return return_value
