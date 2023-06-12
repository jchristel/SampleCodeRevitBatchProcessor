"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Customizable element filter tests which can be used with the custom element filter actions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These tests are used in the custom element filter actions as an argument.

test expects:

- the element of which is the test to be performed against
- the test value

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

from duHast.Revit.Common import worksets as rWork

# import Autodesk
import Autodesk.Revit.DB as rdb


def value_in_name(value, element):
    """
    Check if provided value is in the element name.

    :param value: test value
    :type value: str
    :param element: The element
    :type element: Autodesk.Revit.DB.Element

    :return: True if part of the element name, otherwise False
    :rtype: bool
    """

    return value in rdb.Element.Name.GetValue(element)


def value_equals_workset_name(value, element):
    """
    Check if provided value is equal to the elements workset name.

    :param value: test value
    :type value: str
    :param element: The element
    :type element: Autodesk.Revit.DB.Element

    :return: True if elements workset name matches, otherwise False
    :rtype: bool
    """

    return rWork.is_element_on_workset_by_name(element, value)


def value_in_family_name(value, element):
    """
    Check if provided value is part of the elements Family name.

    :param value: test value
    :type value: str
    :param element: The element
    :type element: Autodesk.Revit.DB.Element

    :return: True if elements family name partly matches, otherwise False
    :rtype: bool
    """

    return value in rdb.Element.Name.GetValue(element.Symbol.Family)

def value_in_element_type_family_name(value, element):
    """
    Check if provided value is part of the element type Family name.

    :param value: test value
    :type value: str
    :param element: The element
    :type element: Autodesk.Revit.DB.Element

    :return: True if elements family name partly matches, otherwise False
    :rtype: bool
    """

    return value in element.Symbol.FamilyName


def value_is_family_name(value, element):
    """
    Check if provided value is equal to the elements Family name.

    :param value: test value
    :type value: str
    :param element: The element
    :type element: Autodesk.Revit.DB.Element

    :return: True if elements family name matches, otherwise False
    :rtype: bool
    """

    return value == rdb.Element.Name.GetValue(element.Symbol.Family)

def value_is_element_type_family_name(value, element):
    """
    Check if provided value is equal to the element type Family name.

    :param value: test value
    :type value: str
    :param element: The element
    :type element: Autodesk.Revit.DB.Element

    :return: True if elements family name matches, otherwise False
    :rtype: bool
    """

    return value == element.Symbol.FamilyName
