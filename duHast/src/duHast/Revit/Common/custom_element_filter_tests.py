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
