"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a base helper functions relating to Revit view types. 
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

import Autodesk.Revit.DB as rdb
from System import Enum


# --------------------------------------------- View Types  ------------------


def _get_view_types(doc):
    """
    Returns all view family types in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ViewFamilyType)
    return collector


def get_view_type_enum_to_name_dict():
    """
    Get a dictionary of the ViewType enum to verbose name e.g. FloorPlan to Floor Plan
    :return: A dictionary in format of Autodesk.Revit.DB.ViewType.FloorPlan: "Floor Plan"
    :rtype: dict
    """
    enum_and_name_dict = {}
    view_type_enum_vals = Enum.GetValues(rdb.ViewType)

    for enum_val in view_type_enum_vals:
        str_val = str(enum_val)
        val_with_spaces = "".join(map(lambda x: x if x.islower() else " " + x, str_val))
        enum_and_name_dict[enum_val] = val_with_spaces.strip()

    return enum_and_name_dict
