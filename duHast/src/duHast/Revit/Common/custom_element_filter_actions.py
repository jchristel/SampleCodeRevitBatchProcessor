"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Customizable element filter actions which can be used with the custom element filter class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thw two action in this module check whether:

- a given property does contain / match a set of test value
- a given property does not contain / match a set of test value


actions expect:

- the test to be performed
- the test values to be performed against
- an output function to pipe any exception message to



"""


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


def action_element_property_contains_any_of_values(test_values, test, output):
    """

    Set up a function checking whether element name contains any of the test values.

    Note:
    If element names does contain any of the test values, the function will return True, Otherwise False.

    :param values: List of values the element name may contain.
    :type values: [str]
    :param output: A function piping the string output to a required location.(console...)
    :type output: func(message)

    """

    def action(doc, element_id):
        flag = False
        try:
            element = doc.GetElement(element_id)
            for value in test_values:
                if test(value, element):
                    flag = True
                    break
        except Exception as e:
            output(
                "action_element_property_contains_values terminated with exception: {}".format(
                    e
                )
            )
            flag = False
        return flag

    return action


def action_element_property_does_not_contains_any_of_values(test_values, test, output):
    """

    Set up a function checking whether element name does not contains any of the test values.

    Note:
    If element names does contain any of the test values, the function will return False, Otherwise True.

    :param values: List of values the element name may not contain.
    :type values: [str]
    :param output: A function piping the string output to a required location.(console...)
    :type output: func(message)
    """

    def action(doc, element_id):
        flag = True
        try:
            element = doc.GetElement(element_id)
            for value in test_values:
                if test(value, element):
                    flag = False
                    break
        except Exception as e:
            output(
                "action_element_property_does_ not_contains_values terminated with exception: {}".format(
                    e
                )
            )
            flag = False
        return flag

    return action
