"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions around families used in system types.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

import Autodesk.Revit.DB as rdb
from duHast.Revit.Common import common as com
from duHast.Revit.MEP_Systems.Utility.MergeLists import merge_into_unique_list
from duHast.Revit.MEP_Systems.Utility.RevitMEPSystemCategories import (
    ROUTING_PREF_RULE_GROUP_TYPES,
)

"""
Properties of system types which can use symbols: (note: RoutingPreferenceManager may contain multiple rules per connection type!)

- Cross
- Elbow
- MultiShapeTransition
- Tap
- Tee
- Transition
- Union

"""


def get_unique_ids_of_used_symbols_from_system_type_id(doc, system_type_id):
    """
    Gets list of unique symbol ids used in a single system type property.
    List can be empty if an exception during processing occurred.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param system_type_id: MEP system type id (pipe, conduit, duct, cable tray)
    :type system_type_id: Autodesk.Revit.DB.ElementId
    :return: List of unique ids representing family symbols used in a system.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    el = doc.GetElement(system_type_id)
    try:
        unfiltered_elements = [
            el.Cross,
            el.Elbow,
            el.MultiShapeTransition,
            el.Tap,
            el.Tee,
            el.Transition,
            el.Union,
        ]
        for unfiltered_element in unfiltered_elements:
            if unfiltered_element != None:
                if (
                    unfiltered_element.Id != rdb.ElementId.InvalidElementId
                    and unfiltered_element.Id not in ids
                ):
                    ids.append(unfiltered_element.Id)
        # check if there is a RoutingPreferenceManager object...it may have some more symbols in its rules
        if el.RoutingPreferenceManager != None:
            # routing manager got a list RoutingReferenceRule objects
            # each of those got a 	MEPPartId property which is what we are after
            rpm = el.RoutingPreferenceManager
            for group in ROUTING_PREF_RULE_GROUP_TYPES:
                # loop over RoutingPreferenceRuleGroupTypes!
                number_of_rules = rpm.GetNumberOfRules(group)
                for i in range(number_of_rules):
                    rule = rpm.GetRule(group, i)
                    if rule.MEPPartId not in ids:
                        ids.append(rule.MEPPartId)

    except Exception as ex:
        print(
            "System type id: {} get used symbol ids threw exception: {}".format(
                system_type_id, ex
            )
        )
    return ids


def get_unique_ids_of_used_symbols_from_system_type_ids(doc, system_type_ids):
    """
    Gets a list of unique symbol ids used in these MEP system type properties:
    - Cross
    - Elbow
    - MultiShapeTransition
    - Tap
    - Tee
    - Transition
    - Union
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param system_type_ids: List of MEP system type id belonging to pipe, conduit, duct or cable tray.
    :type system_type_ids: List Autodesk.Revit.DB.ElementId
    :return: List of unique ids representing family symbols used in mep systems.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    for system_type_id in system_type_ids:
        ids_unfiltered = get_unique_ids_of_used_symbols_from_system_type_id(
            doc, system_type_id
        )
        ids = merge_into_unique_list(ids, ids_unfiltered)
    return ids


# --------------------------------------- symbols available in model -------------------------------


def get_symbol_ids_of_mep_system_types(doc, category_list, system_type_name):
    """
    Gets list of symbol ids belonging to provided categories loaded in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param category_list: List of built in categories to filter symbols by.
    :type category_list: list Autodesk.Revit.DB.BuiltInCategory
    :param system_type_name: Used in exception message to identify the mep system
    :type system_type_name: str
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    try:
        multi_cat_filter = rdb.ElementMulticategoryFilter(category_list)
        col = (
            rdb.FilteredElementCollector(doc)
            .OfClass(rdb.FamilySymbol)
            .WherePasses(multi_cat_filter)
        )
        ids = com.get_ids_from_element_collector(col)
    except Exception as ex:
        print(system_type_name + " threw exception: " + str(ex))
    return ids
