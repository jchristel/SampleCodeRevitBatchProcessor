"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Element id functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
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
from Autodesk.Revit.DB import ElementId


def get_el_id(el):
    """
    Gets the ID of a Revit element.
    :param el: The Revit element.
    :return: The ID of the element.
    :rtype: int
    """

    if el:
        el_id = getattr(el, "Id", None)
        if el_id:
            return el_id
        else:
            raise ValueError("Element provided does not have an Id attribute.")
    else:
        raise ValueError("Element is None, cannot get ID.")


def get_el_id_int(el):
    """
    Gets the integer ID of a Revit element.
    :param el: The Revit element.
    :return: The integer ID of the element.
    :rtype: int

    """
    if not isinstance(el, ElementId):
        el_id = get_el_id(el)
    else:
        el_id = el

    if getattr(el_id, "IntegerValue", None):
        return int(el_id.IntegerValue)
    elif getattr(el_id, "Value", None):
        return int(el_id.Value)
    else:
        raise ValueError("Element ID does not have an IntegerValue or Value attribute.")
