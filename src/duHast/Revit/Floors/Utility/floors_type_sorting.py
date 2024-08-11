"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit floor utility functions. 
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

from duHast.Revit.Floors.Utility import floors_filter as rFloorsFilter


def build_floor_type_dictionary(collector, dic):
    """
    Returns the dictionary past in with keys and or values added retrieved from collector past in.
    Keys are built in floor family type names.
    TODO: This code repeats across a number of modules. Use generic instead!
    :param collector: A filtered element collector containing floor types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: A dictionary containing key: floor type family name, value: list of ids belonging to that type.
    :type dic: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    :return: A dictionary containing key: built in floor type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    """

    for c in collector:
        if c.FamilyName in dic:
            if c.Id not in dic[c.FamilyName]:
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic


def sort_floor_types_by_family_name(doc):
    """
    Returns a dictionary containing all floor types in the model.
    Key values are as per BUILTIN_FLOOR_TYPE_FAMILY_NAMES.
    TODO: This code repeats across a number of modules. Use generic instead!
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A dictionary containing key: floor type family name, value: list of ids.
    :rtype: dic { str: [Autodesk.Revit.DB.ElementId]}
    """

    # get all floor Type Elements
    wts = rFloorsFilter._get_floor_types_by_class(doc)
    # get all floor types including in place floor families
    wts_two = rFloorsFilter._get_all_floor_types_by_category(doc)
    used_wts = {}
    used_wts = build_floor_type_dictionary(wts, used_wts)
    used_wts = build_floor_type_dictionary(wts_two, used_wts)
    return used_wts
