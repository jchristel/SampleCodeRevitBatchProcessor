'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Common Revit API utility functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
#License:
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

#import datetime
import System
import clr


clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

#import glob
# class used for stats reporting

# import everything from Autodesk Revit DataBase namespace (Revit API)
import Autodesk.Revit.DB as rdb
import os.path as path
# utilities
from duHast.Utilities import Utility as util
from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet
# importing revit groups module
from duHast.APISamples.Common import RevitGroups as rGroup


def get_element_mark(e):
    '''
    Returns the mark value of an element.

    :param e: The element.
    :type e: Autodesk.Revit.DB.Element

    :return:
        The element mark value.  
        If an exception occurred, the message will be 'Failed with exception: ' + the exception string.
    :rtype: str
    '''

    mark = ''
    try:
        paraMark = e.get_Parameter(rdb.BuiltInParameter.ALL_MODEL_MARK)
        mark = '' if paraMark == None else paraMark.AsString()
    except Exception as e:
        mark = 'Failed with exception: ' + str(e)
    return mark

#----------------------------------------Legend Components -----------------------------------------------

def get_legend_components_in_model(doc, typeIds):
    ''' 
    Returns all symbol (type) ids of families which have been placed as legend components and have match in list past in.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param typeIds: List of typeIds to check against.
    :type typeIds: list str
    :raise: Any exception will need to be managed by the function caller.

    :return: Values are representing symbol (type) ids of legend components in models filtered by ids past in.
    :rtype: list of str
    '''

    ids = []
    # get all legend components in the model to check against list past in
    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_LegendComponents)
    for c in col:
        id = rParaGet.get_built_in_parameter_value (c, rdb.BuiltInParameter.LEGEND_COMPONENT, rParaGet.get_parameter_value)
        if (id in typeIds and id not in ids):
            ids.append(id)
            break
    return ids

#----------------------------------------types - Autodesk.Revit.DB ElementType -----------------------------------------------

def get_similar_type_families_by_type(doc, typeGetter):
    '''
    Returns a list of unique types its similar family (symbol) types.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param function typeGetter:
        The function which takes the document as an argument and returns a list of family symbols (types).
    :raise: Any exception will need to be managed by the function caller.
    
    :return: list of Autodesk.Revit.DB.Symbol and Autodesk.Revit.DB.ElementId:
    :rtype: List [[Autodesk.Revit.DB.ElementType, Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...],]
    '''

    simTypes=[]
    types = typeGetter(doc)
    for t in types:
        tData = [t]
        sims = t.GetSimilarTypes()
        simData = []
        for sim in sims:
            simData.append(sim)
        # simData.sort() # not sure a sort is actually doing anything
        tData.append(simData)
        if(check_unique_type_data(simTypes, tData)):
            simTypes.append(tData)
    return simTypes

def check_unique_type_data(existingTypes, newTypeData):
    '''
    Compares two lists of types and their similar types (ids).

    Assumes that second list past in has only one occurrence of type and its similar types
    Compares types by name and if match their similar types.

    :param existingTypes: Source list
    :type existingTypes: List of List in format [[Autodesk.Revit.DB.ElementType , Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...],]
    :param newTypeData: Comparison list
    :type newTypeData: List in format [Autodesk.Revit.DB.ElementType, Autodesk.Revit.DB.ElementId, Autodesk.Revit.DB.ElementId,...] 
    
    :return: 
        True, if new type is not in list existing Types passed in or
        if ids of similar family types do not match any similar types already in list
    :rtype: bool
    '''

    result = True
    for s in existingTypes:
        # check for matching family name
        if (s[0].FamilyName == newTypeData[0].FamilyName):
            # check if match has the same amount of similar family types
            # if not it is unique
            if (len(s[1]) == len(newTypeData[1])):
                # assume IDs do match
                matchIDs = True
                for i in range(len(s[1])):
                    if(s[1][i] != newTypeData[1][i]):
                          # id's dont match, this is unique
                          matchIDs = False
                          break
                if(matchIDs):
                    # data is not unique
                    result = False
                    break
    return result

def get_unused_type_ids_in_model(doc, typeGetter, instanceGetter):
    '''
    Returns ID of unused family types in the model.

    Used in purge code since it leaves at least one type behind (built in families require at least one type in the model)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param typeGetter: Function accepting current document as argument and returning a collector of types in model
    :type typeGetter: func
    :param instanceGetter: Function accepting current document as argument and returning a list of instances in model
    :type instanceGetter: func
    
    :return: List of type ids which can be purged from the model.
    :rtype: list Autodesk.Revit.DB.ElementId
    '''
    
    # get all  types available and associated family types
    familyTypesAvailable = get_similar_type_families_by_type(doc, typeGetter)
    # get used type ids
    usedFamilyTypeIds = instanceGetter(doc)
    # flag indicating that at least one type was removed from list because it is in use
    # this flag used when checking how many items are left...
    removedAtLeastOne = []
    # set index to 0, type names might not be unique!!
    counter = 0
    # loop over available types and check which one is used
    for t in familyTypesAvailable:
        # remove all used family type Id's from the available list...
        # whatever is left can be deleted if not last available item in list for type
        # there should always be just one match
        for usedFamilyTypeId in usedFamilyTypeIds:
            # get the index of match
            index = util.IndexOf(t[1],usedFamilyTypeId)
            # remove used item from list
            if (index > -1):
                t[1].pop(index)
                if(t not in removedAtLeastOne):
                    removedAtLeastOne.append(counter)
        counter = counter + 1
    # filter these by family types where is only one left
    # make sure to leave at least one family type behind, since the last type cannot be deleted
    filteredUnusedTypeIds = []
    # reset index
    counter = 0
    for t in familyTypesAvailable:
        if (counter in removedAtLeastOne):
            # at least one item was already removed from list...so all left over ones can be purged
            for id in t[1]:
                # get the element
                tFam = doc.GetElement(id)
                if (tFam.CanBeDeleted):
                    filteredUnusedTypeIds.append(id)
        else:
            # need to keep at least one item
            if(len(t[1]) > 1):
                #maxLength = len(t[1])
                # make sure to leave the first one behind to match Revit purge behavior
                for x in range(1, len(t[1])):
                    id = t[1][x]
                    # get the element
                    tFam = doc.GetElement(id)
                    # check whether this can be deleted...
                    if (tFam.CanBeDeleted):
                        filteredUnusedTypeIds.append(id)
        counter = counter + 1 
    return filteredUnusedTypeIds

#----------------------------------------instances of types - Autodesk.Revit.DB ElementType -----------------------------------------------

def get_not_placed_types(doc, getTypes, getInstances):
    '''
    
    returns a list of unused types foo by comparing type Ids of placed instances with types past in.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param getTypes: Types getter function. Needs to accept doc as argument and return a collector of type foo
    :type getTypes: func (doc)
    :param getInstances: Instances getter function. Needs to accept doc as argument and return a collector of instances foo
    :type getInstances: func(doc)
    
    :return: returns a list of unused types
    :rtype: list of type foo
    '''

    availTypes = getTypes(doc)
    placedInstances = getInstances(doc)
    notPlaced = []
    alreadyChecked = []
    # loop over all types and check for matching instances
    for at in availTypes:
        match = False
        for pi in placedInstances:
            # check if we had this type checked already, if so ignore and move to next
            if(pi.GetTypeId() not in alreadyChecked):
                #  check for type id match
                if(pi.GetTypeId() == at.Id):
                    # add to already checked and verified as match list
                    alreadyChecked.append(pi.GetTypeId())
                    match = True
                    break
        if(match == False):
            notPlaced.append(at)
    return notPlaced

# --------------------------------------------- check whether groups contain certain element types - Autodesk.Revit.DB ElementType  ------------------

def check_group_for_type_ids(doc, groupType, typeIds):
    '''
    
    Filters passed in list of type ids by type ids found in group and returns list of unmatched Id's
    
    This only returns valid data if at least one instance of the group is placed in the model, otherwise GetMemberIds() returns empty!!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param groupTypes: Group to be checked whether they contains elements of types past in.
    :type groupTypes: Autodesk.Revit.DB.GroupType
    :param typeIds: List of type ids to confirm whether they are in use a group
    :type typeIds: list of Autodesk.Revit.Db.ElementId
    
    :return: Returns all type ids not matched
    :rtype: list of Autodesk.Revit.Db.ElementId
    '''

    unusedTypeIds = []
    usedTypeIds = []
    # get the first group from the group type and get its members
    for g in groupType.Groups:
        # get ids of group elements:
        memberIds = g.GetMemberIds()
        # built list of used type ids
        for memberId in memberIds:
            member = doc.GetElement(memberId)
            usedTypeId = member.GetTypeId()
            if (usedTypeId not in usedTypeIds):
                usedTypeIds.append(usedTypeId)
    for checkId in typeIds:
        if(checkId not in usedTypeIds):
            unusedTypeIds.append(checkId)
    return unusedTypeIds

def check_groups_for_matching_type_ids(doc, groupTypes, typeIds):
    '''
    Checks all elements in groups past in whether group includes element of which type Id is matching any type ids past in
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param groupTypes: Groups to be checked whether they contains elements of types past in.
    :type groupTypes: list of Autodesk.Revit.DB.GroupType
    :param typeIds: List of type ids to confirm whether they are in use a group
    :type typeIds: list of Autodesk.Revit.Db.ElementId
    
    :return: Returns all type ids not matched
    :rtype: list of Autodesk.Revit.Db.ElementId
    '''

    for groupType in groupTypes:
        typeIds = check_group_for_type_ids(doc, groupType, typeIds)
        # check if all type ids where matched up
        if (len(typeIds) == 0):
            break
    return typeIds

def get_unused_type_ids_from_detail_groups(doc, typeIds):
    '''
    Checks elements in nested detail groups and detail groups whether their type ElementId is in the list past in.
    
    This only returns valid data if at least one instance of the group is placed in the model!!!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param typeIds: List of type ids to confirm whether they are in use a group
    :type typeIds: list of Autodesk.Revit.Db.ElementId
    
    :return: Returns all type Ids from list past in not found in group definitions
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    unusedTypeIds = []
    nestedDetailGroups = rGroup.get_nested_detail_groups(doc)
    detailGroups = rGroup.get_detail_groups(doc)
    unusedTypeIds = check_groups_for_matching_type_ids(doc, nestedDetailGroups, typeIds)
    unusedTypeIds = check_groups_for_matching_type_ids(doc, detailGroups, typeIds)
    return unusedTypeIds

#----------------------------------------elements-----------------------------------------------

def get_ids_from_element_collector(col):
    '''
    This will return a list of all element ids in collector.

    Any element in collector which is invalid will be ignored.
    
    :param col: A filtered element collector.
    :type col: Autodesk.Revit.DB.FilteredElementCollector 
    
    :return: list of all element ids of valid elements in collector.
    :rtype: List of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    for c in col:
        try:   
            ids.append(c.Id)
        except Exception as e:
            pass
    return ids