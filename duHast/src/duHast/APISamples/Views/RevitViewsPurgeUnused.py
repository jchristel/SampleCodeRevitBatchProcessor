'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Views purge unused utilities.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
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
from duHast.APISamples.Family import RevitFamilyUtils as rFamUPurge
from duHast.APISamples.Views import RevitViewReferencing as rViewRef
from duHast.APISamples.Views.Utility.ViewTypes import _get_view_types
from duHast.APISamples.Family import PurgeUnusedFamilyTypes as rFamPurge


# view reference purging

def get_unused_continuation_marker_type_ids_for_purge(doc):
    '''
    Gets all unused view continuation type ids in model for purge.
    This method can be used to safely delete all unused view continuation marker types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    all_available_type_ids = rViewRef.get_all_view_continuation_type_ids(doc)
    all_used_type_ids = rViewRef.get_used_view_continuation_type_ids(doc)
    for a_id in all_available_type_ids:
        if( a_id not in all_used_type_ids):
            ids.append(a_id)
    return ids


def is_nested_family_symbol(doc, id, nested_family_names):
    '''
    Returns true if symbol belongs to family in list past in.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param id: The element id of a symbol.
    :type id: Autodesk.Revit.DB.ElementId
    :param nested_family_names: list of family names know to be nested families.
    :type nested_family_names: list str
    :return: True if family name derived from symbol is in list past in, otherwise False.
    :rtype: bool
    '''

    flag = False
    fam_symbol = doc.GetElement(id)
    fam = fam_symbol.Family
    if(fam.Name in nested_family_names):
        flag = True
    return flag


def get_unused_view_ref_and_continuation_marker_symbol_ids(doc):
    '''
    Gets the ids of all view reference symbols(types) and view continuation symbols (types) not used in the model.
    Not used: These symbols are not used in any view reference types, or nested in any symbols used in view reference types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    # compare used vs available in view ref types
    # whatever is marked as unused: check for any instances in the model...placed on legends!
    available_ids = rViewRef.get_all_view_reference_symbol_ids(doc) # check: does this really return all continuation marker types??
    used_ids = rViewRef.get_used_view_reference_and_continuation_marker_symbol_ids(doc)
    # elevation marker families might use nested families...check!
    nested_family_names = rViewRef.get_nested_family_marker_names(doc, used_ids)
    check_ids = []
    for a_id in available_ids:
        if (a_id not in used_ids):
            check_ids.append(a_id)
    # check for any instances
    for id in check_ids:
        instances = rFamUPurge.get_family_instances_by_symbol_type_id(doc, id).ToList()
        if(len(instances) == 0):
            if(is_nested_family_symbol(doc, id, nested_family_names) == False):
                ids.append(id)
    return ids


def get_unused_view_ref_and_continuation_marker_families_for_purge(doc):
    '''
    Gets the ids of all view reference symbols(types) ids and or family ids not used in the model for purging.
    This method can be used to safely delete all unused view reference and continuation marker family symbols\
        or families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    return rFamPurge.get_unused_in_place_ids_for_purge(doc, get_unused_view_ref_and_continuation_marker_symbol_ids)

def get_unused_view_reference_type_ids_for_purge(doc):
    '''
    Gets all unused view references type ids in model for purge.
    This method can be used to safely delete all unused view reference types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    ids = []
    all_available_type_ids = rViewRef.get_all_view_reference_type_id_data(doc)
    all_used_type_ids = rViewRef.get_used_view_reference_type_id_data(doc)
    for key,value in all_available_type_ids.items():
        if(all_used_type_ids.has_key(key)):
            for available_type_id in all_available_type_ids[key]:
                if(available_type_id not in all_used_type_ids[key]):
                    ids.append(available_type_id)
        else:
            # add all types under this key to be purge list...might need to check whether I need to leave one behind...
            if(len(all_available_type_ids[key])>0):
                ids = ids + all_available_type_ids[key]
    return ids


# view types purging

def get_used_view_type_ids(doc):
    '''
    Returns all view family types in use in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: ids of view family types in use
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    view_type_ids_used = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
    for v in col:
        # filter out browser organization and other views which cant be deleted
        if(v.IsTemplate == False and
        v.ViewType != rdb.ViewType.SystemBrowser and
        v.ViewType != rdb.ViewType.ProjectBrowser and
        v.ViewType != rdb.ViewType.Undefined and
        v.ViewType != rdb.ViewType.Internal and
        v.ViewType != rdb.ViewType.DrawingSheet):
            if(v.GetTypeId() not in view_type_ids_used):
                view_type_ids_used.append(v.GetTypeId())
    return view_type_ids_used


def get_unused_view_type_ids(doc):
    '''
    Returns all unused view family types in the model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: ids of view family types not in use
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    filtered_unused_view_type_ids = com.get_unused_type_ids_in_model(doc, _get_view_types, get_used_view_type_ids)
    return filtered_unused_view_type_ids