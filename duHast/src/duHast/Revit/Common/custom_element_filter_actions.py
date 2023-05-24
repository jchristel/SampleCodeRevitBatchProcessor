"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Customizable element filter actions which can be used with the custom element filter class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
# Copyright (c) 2020  Jan Christel
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


def action_element_name_contains_any_of_values(test_values, test, output):
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
                "action_element_name_contains_values terminated with exception: {}".format(
                    e
                )
            )
            flag = False
        return flag

    return action


def action_element_name_does_not_contains_any_of_values(test_values, test, output):
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
                "action_element_name_does_ not_contains_values terminated with exception: {}".format(
                    e
                )
            )
            flag = False
        return flag

    return action
