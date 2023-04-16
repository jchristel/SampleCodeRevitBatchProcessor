'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions around families used in system types.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

import Autodesk.Revit.DB as rdb
from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.MEP_Systems.Utility.MergeLists import merge_into_unique_list
from duHast.APISamples.MEP_Systems.Utility.RevitMEPSystemCategories import ROUTING_PREF_RULE_GROUP_TYPES

'''
Properties of system types which can use symbols: (note: RoutingPreferenceManager may contain multiple rules per connection type!)

- Cross
- Elbow
- MultiShapeTransition
- Tap
- Tee
- Transition
- Union

'''

def get_unique_ids_of_used_symbols_from_system_type_id(doc, systemTypeId):
    '''
    Gets list of unique symbol ids used in a single system type property.
    List can be empty if an exception during processing occurred.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param systemTypeId: MEP system type id (pipe, conduit, duct, cable tray)
    :type systemTypeId: Autodesk.Revit.DB.ElementId
    :return: List of unique ids representing family symbols used in a system.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    el = doc.GetElement(systemTypeId)
    try:
        unfilteredElements = [el.Cross, el.Elbow, el.MultiShapeTransition, el.Tap, el.Tee, el.Transition, el.Union]
        for unfilteredElement in unfilteredElements:
            if (unfilteredElement != None):
                if (unfilteredElement.Id != rdb.ElementId.InvalidElementId and unfilteredElement.Id not in ids):
                    ids.append(unfilteredElement.Id)
        #check if there is a RoutingPreferenceManager object...it may have some more symbols in its rules
        if(el.RoutingPreferenceManager != None):
            # routing manager got a list RoutingReferenceRule objects
            # each of those got a 	MEPPartId property which is what we are after
            rpm = el.RoutingPreferenceManager
            for group in ROUTING_PREF_RULE_GROUP_TYPES:
                # loop over RoutingPreferenceRuleGroupTypes!
                numberOfRules = rpm.GetNumberOfRules(group)
                for i in range(numberOfRules):
                    rule = rpm.GetRule(group, i)
                    if rule.MEPPartId not in ids:
                        ids.append(rule.MEPPartId)


    except Exception as ex:
        print('System type get used symbol ids threw exception: '+ str(ex))
    return ids


def get_unique_ids_of_used_symbols_from_system_type_ids(doc, systemTypeIds):
    '''
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
    :param systemTypeIds: List of MEP system type id belonging to pipe, conduit, duct or cable tray.
    :type systemTypeIds: List Autodesk.Revit.DB.ElementId
    :return: List of unique ids representing family symbols used in mep systems.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    for systemTypeId in systemTypeIds:
        idsUnfiltered = get_unique_ids_of_used_symbols_from_system_type_id(doc, systemTypeId)
        ids = merge_into_unique_list(ids, idsUnfiltered)
    return ids


# --------------------------------------- symbols available in model -------------------------------

def get_symbol_ids_of_mep_system_types(doc, categoryList, systemTypeName):
    '''
    Gets list of symbol ids belonging to provided categories loaded in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param categoryList: List of built in categories to filter symbols by.
    :type categoryList: list Autodesk.Revit.DB.BuiltInCategory
    :param systemTypeName: Used in exception message to identify the mep system
    :type systemTypeName: str
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    try:
        multiCatFilter = rdb.ElementMulticategoryFilter(categoryList)
        col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(multiCatFilter)
        ids = com.get_ids_from_element_collector (col)
    except Exception as ex:
        print (systemTypeName+ ' threw exception: ' + str(ex))
    return ids