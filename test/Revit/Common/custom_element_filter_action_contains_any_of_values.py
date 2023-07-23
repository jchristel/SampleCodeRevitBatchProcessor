"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a custom element filter action of type: property contains any of values tests . 
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

from test.Revit.TestUtils import revit_test
from duHast.Revit.Common.custom_element_filter_actions import (
    action_element_property_contains_any_of_values,
)
from duHast.Revit.Common.custom_element_filter_tests import (
    value_in_name,
    value_in_family_name,
    value_is_family_name,
    value_equals_workset_name,
    value_in_element_type_family_name,
    value_is_element_type_family_name,
)
from duHast.Utilities.Objects import result as res

# import Autodesk
import Autodesk.Revit.DB as rdb

# rbp required!
import revit_script_util

from collections import namedtuple


"""
Tuple containing test settings.
"""

SETTINGS_DATA = namedtuple(
    "settings_data", "element_id test_values test expected_result"
)


class CustomElementFilterActionPropertyContains(revit_test.RevitTest):
    def __init__(self, doc):
        # store document in base class
        super(CustomElementFilterActionPropertyContains, self).__init__(
            doc=doc, test_name="property_contains_any_of_values"
        )

    def _output(self, message):
        # Custom output implementation
        revit_script_util.Output(message)

    def test(self):
        """
        name_contains_any_of_values

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param test_name: The test name.
        :type test_name: str

        :return:
            Result class instance.
                - .result = True if name tests past, otherwise False.
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
            # Create a test list of values
            data_set = (
                SETTINGS_DATA(
                    968295, ["value1", "value2", "value3"], value_in_name, False
                ),  # this is a text note instance, name is 'Text Note 1'
                SETTINGS_DATA(
                    968295, ["value1", "Note", "value3"], value_in_name, True
                ),  # this is a text note instance, name is 'Text Note 1'
                SETTINGS_DATA(
                    968295, ["value1", "value2", "value3"], value_in_family_name, False
                ),  # this is a text note instance, family does not exist on its type
                SETTINGS_DATA(
                    968295, ["value1", "value2", "value3"], value_is_family_name, False
                ),  # this is a text note instance, family does not exist on its type
                SETTINGS_DATA(
                    968295,
                    ["value1", "value2", "value3"],
                    value_in_element_type_family_name,
                    False,
                ),  # this is a text note instance, family element type name is 'Text'
                SETTINGS_DATA(
                    968295,
                    ["value1", "ex", "value3"],
                    value_in_element_type_family_name,
                    True,
                ),  # this is a text note instance, family element type name is 'Text'
                SETTINGS_DATA(
                    968295,
                    ["value1", "value2", "value3"],
                    value_is_element_type_family_name,
                    False,
                ),  # this is a text note instance, family element type name is 'Text'
                SETTINGS_DATA(
                    968295,
                    ["value1", "Text", "value3"],
                    value_is_element_type_family_name,
                    True,
                ),  # this is a text note instance, family element type name is 'Text'
                SETTINGS_DATA(
                    968295,
                    ["value1", "value2", "value3"],
                    value_equals_workset_name,
                    False,
                ),  # this is a text note instance, there is no workset in the test file
            )

            for data in data_set:
                # Create the action function
                action = action_element_property_contains_any_of_values(
                    test_values=data.test_values, test=data.test, output=self._output
                )

                # Execute the action
                result = action(self.document, rdb.ElementId(data.element_id))

                # store result vs expected result
                return_value.append_message(
                    " {} vs {} test values: {}".format(result, data.expected_result, data.test_values)
                )

                # check the outcome
                assert result == data.expected_result

        except Exception as e:
            return_value.update_sep(
                False,
                "An exception occurred in function {}: {}".format(self.test_name, e),
            )

        return return_value
