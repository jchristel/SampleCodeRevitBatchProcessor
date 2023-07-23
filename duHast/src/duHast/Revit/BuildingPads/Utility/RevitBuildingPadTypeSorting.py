"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to sorting Revit building pads by types. 
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

from duHast.Revit.BuildingPads.Utility import (
    RevitBuildingPadsFilter as rBuildingPadFilter,
)


def build_building_pad_type_dictionary(collector, dic):
    """
    Returns the dictionary past in with keys and or values added retrieved from collector past in.
    Keys are built in building pad family type names.
    TODO: Use more generic code.
    :param collector: A filtered element collector containing building pad types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: A dictionary containing key:  building pad type family name, value: list of ids belonging to that type.
    :type dic: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    :return: A dictionary containing key: built in building pad type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    """

    for c in collector:
        if dic.has_key(c.FamilyName):
            if c.Id not in dic[c.FamilyName]:
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic


def sort_building_pad_types_by_family_name(doc):
    """
    Returns a dictionary of all building pad types in the model where key is the build in wall family name, values are ids of associated wall types.
    TODO: Use more generic code.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A dictionary containing key: built in building pad type family name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    """

    # get all building pad Type Elements
    wts = rBuildingPadFilter._get_building_pad_types_by_class(doc)
    # get all pad types including in place pad families
    wts_two = rBuildingPadFilter._get_all_building_pad_types_by_category(doc)
    usedWts = {}
    usedWts = build_building_pad_type_dictionary(wts, usedWts)
    usedWts = build_building_pad_type_dictionary(wts_two, usedWts)
    return usedWts
