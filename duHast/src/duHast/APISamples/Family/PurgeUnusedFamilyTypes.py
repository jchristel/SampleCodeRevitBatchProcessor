'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to purging Revit family types. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
from duHast.APISamples.Common import RevitPurgeUtils as rPurgeUtils
from duHast.Utilities import Utility as util
from duHast.APISamples.Family.RevitFamilyUtils import get_family_symbols_ids, get_symbols_from_type
from duHast.APISamples.Family.Utility.LoadableFamilyCategories import CATEGORIES_LOADABLE_TAGS, CATEGORIES_LOADABLE_3D


def family_all_types_in_use(famTypeIds, usedTypeIds):
    ''' 
    Checks if symbols (types) of a family are in use in a model.
    Check is done by comparing entries of famTypeIds with usedTypeIds.
    :param famTypeIds: list of symbol(type) ids of a family
    :type famTypeIds: list Autodesk.Revit.DB.ElementId
    :param  usedTypeIds: list of symbol(type) ids in use in a project
    :type usedTypeIds: list Autodesk.Revit.DB.ElementId
    :return: False if a single symbol id contained in list famTypeIds has a match in list usedTypeIds, otherwise True.
    :rtype: bool
    '''

    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in usedTypeIds):
            match = False
            break
    return match

def get_unused_in_place_ids_for_purge(doc, unusedTypeGetter):
    '''
    Filters symbol(type) ids and family ids (when not a single type of given family is in use) of families.
    The returned list of ids can be just unused family symbols or entire families if none of their symbols are in use.
    in terms of purging its faster to delete an entire family definition rather then deleting it's symbols first and then the 
    definition.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param unusedTypeGetter: 
        A function returning ids of unused symbols (family types) as a list. 
        It requires as argument the current model document only.
    :type unusedTypeGetter: function (doc) -> list Autodesk.Revit.DB.ElementId
    :return: A list of Element Ids representing the family symbols and or family id's matching filter.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''

    unusedIds = []
    unusedFamilyIds = []
    # get all unused type Ids
    unusedTypeIds = unusedTypeGetter(doc)
    # get family Elements belonging to those type ids
    families = get_symbols_from_type(doc, unusedTypeIds)
    # check whether an entire family can be purged and if so remove their symbol(type) ids from 
    # from unusedType ids list since we will be purging the family instead
    for key, value in families.items():
        if(family_all_types_in_use(value, unusedTypeIds)):
            unusedFamilyIds.append(key)
            unusedTypeIds = util.RemoveItemsFromList(unusedTypeIds, value)
    # check whether entire families can be purged and if so add their ids to list to be returned
    if(len(unusedFamilyIds)>0):
        unusedIds = unusedFamilyIds + unusedTypeIds
    else:
        unusedIds = unusedTypeIds
    return unusedIds


def get_used_unused_type_ids(doc, typeIdGetter, useType = 0, excludeSharedFam = True):
    '''
    Filters types obtained by past in typeIdGetter method and depending on useType past in returns either the used or unused symbols of a family
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param typeIdGetter: 
        A function returning ids of symbols (family types) as a list, requires as argument: 
        the current model doc, 
        ICollection of built in categories, 
        bool: exclude shared families
    :type typeIdGetter: function (doc, ICollection, bool) -> list[Autodesk.Revit.DB.ElementId]
    :param useType: 0, no dependent elements (not used); 1: has dependent elements(is in use)
    :type useType: int
    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    # get all types elements available
    allLoadableThreeDTypeIds = typeIdGetter(doc, CATEGORIES_LOADABLE_3D, excludeSharedFam)
    allLoadableTagsTypeIds = typeIdGetter(doc, CATEGORIES_LOADABLE_TAGS, excludeSharedFam)
    allTypeIds = allLoadableThreeDTypeIds + allLoadableTagsTypeIds
    ids = []
    for typeId in allTypeIds:
        type = doc.GetElement(typeId)
        hasDependents = rPurgeUtils.has_dependent_elements(doc, type)
        if(hasDependents == useType):
            ids.append(typeId)
    return ids


def get_unused_family_types(doc, excludeSharedFam = True):
    '''
    Filters unused non shared family (symbols) type ids in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param excludeSharedFam: Default is True (exclude any shared families from filter result)
    :type excludeSharedFam: bool
    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = get_used_unused_type_ids(doc, get_family_symbols_ids, 0, excludeSharedFam)
    return ids


def get_unused_non_shared_family_symbols_and_type_ids_to_purge(doc):
    '''
    Filters unused, non shared and in place family (symbols) type ids in model which can be purged from the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of Element Ids representing the family symbols matching filter.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    idsUnused = get_unused_in_place_ids_for_purge(doc, get_unused_family_types)
    return idsUnused