'''
This module contains a number of functions around Revit detail items. 
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2021  Jan Christel
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

import clr
import System

# import common library modules
import RevitCommonAPI as com
import RevitFamilyUtils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_GROUPS_HEADER = ['HOSTFILE','ID', 'ITEM TYPE']

# --------------------------------------------- utility functions ------------------

# returns a list of filled region elements from the model
# doc   current document
def GetFilledRegionsInModel(doc):
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FilledRegion).ToList()


ELEMENT_TYPE = 'Autodesk.Revit.DB.ElementType'
FILLED_REGION_TYPE = 'Autodesk.Revit.DB.FilledRegionType'
FAMILY_SYMBOL = 'Autodesk.Revit.DB.FamilySymbol'

DETAIL_COMPONENT_TYPES = [
    ELEMENT_TYPE,
    FILLED_REGION_TYPE,
    FAMILY_SYMBOL
]

# doc:   current model document
def GetAllDetailTypesByCategory(doc):
    ''' this will return a filtered element collector of all detail component types in the model'''
    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_DetailComponents).WhereElementIsElementType()
    return collector

# collector   filtered element collector detail component types
def BuildDetailTypeIdsDictionary(collector):
    '''returns the dictionary keys is autodesk.revit.db element type as string and values are available type ids'''
    dic = {}
    for c in collector:
        if(dic.has_key(str(c.GetType()))):
            if(c.Id not in dic[str(c.GetType())]):
                dic[str(c.GetType())].append(c.Id)
        else:
            dic[str(c.GetType())] = [c.Id]
    return dic

# doc:   current model document
# collector   filtered element collector detail component types
def BuildDependentElementsDictionary(doc, collector):
    '''returns the dictionary keys is autodesk.revit.db element type as string and values are elements'''
    dic = {}
    for c in collector:
        el = doc.GetElement(c)
        if(dic.has_key(str(el.GetType()))):
            if(c not in dic[str(el.GetType())]):
                dic[str(el.GetType())].append(c)
        else:
            dic[str(el.GetType())] = [c]
    return dic
    
# -------------------------------- repeating detail types -------------------------------------------------------

# doc:   current model document
def GetAllRepeatingDetailTypeIdsAvailable(doc):
    '''get all repeating detail types in model'''
    dic = BuildDetailTypeIdsDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(ELEMENT_TYPE)):
        return dic[ELEMENT_TYPE]
    else:
        return []

# doc   current document
def GetUsedRepeatingDetailTypeIds(doc):
    '''get all used repeating detail type ids'''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRepeatingDetailTypeIdsAvailable, 1, 1)
    return ids

# doc   current document
def GetUnUsedRepeatingDetailTypeIds(doc):
    '''get all unused repeating detail type ids'''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRepeatingDetailTypeIdsAvailable, 0, 1)
    return ids

# doc   current document
def GetUnUsedRepeatingDetailTypeIdsForPurge(doc):
    '''get all unused repeating detail type ids'''
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRepeatingDetailTypeIdsAvailable, 0, 1)
    allIds = GetAllRepeatingDetailTypeIdsAvailable(doc)
    # need to keep at least one
    if(len(allIds) == len(ids)):
        ids.pop(0)
    return ids

# -------------------------------- Detail families -------------------------------------------------------

# doc:   current model document
def GetAllDetailSymbolIdsAvailable(doc):
    '''get all detail symbol types in model'''
    dic = BuildDetailTypeIdsDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(ELEMENT_TYPE)):
        return dic[FAMILY_SYMBOL]
    else:
        return []

# doc:   current model document
# idsRepeatDet:   repeating detail types
def GetDetailSymbolsUsedInRepeatingDetails(doc, idsRepeatDet):
    '''returns the ids of all symbols used in repeating details'''
    ids = []
    for idR in idsRepeatDet:
        repeatDetail = doc.GetElement(idR)
        id = com.GetBuiltInParameterValue(repeatDetail, rdb.BuiltInParameter.REPEATING_DETAIL_ELEMENT)
        if(id not in ids and id != rdb.ßElementId.InvalidElementId and id != None):
            ids.append(id)
    return ids

# doc:   current model document
def GetAllUsedDetailSymbolIds(doc):
    '''get all used detail symbol type ids in model'''
    ids = []
    dic = BuildDetailTypeIdsDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(ELEMENT_TYPE)):
        idsUnfiltered = dic[FAMILY_SYMBOL]
        # check if used in repeating details
        idsRepeatDet = GetAllRepeatingDetailTypeIdsAvailable(doc)
        #print('ids used in repeating details ' + str(len(idsRepeatDet)))
        # get detail types used in repeating details only
        idsOfDetailsUsedRepeatDetails = GetDetailSymbolsUsedInRepeatingDetails(doc, idsRepeatDet)
        # get detail types used in model
        idsUsedInModel = com.GetUsedUnusedTypeIds(doc, GetAllDetailSymbolIdsAvailable, 1)
        print('ids used in model ' + str(len(idsUsedInModel)))
        # built overall ids list
        for id in idsOfDetailsUsedRepeatDetails:
            if (id not in ids):
                ids.append(id)
        for id in idsUsedInModel:
            if(id not in ids):
                ids.append(id)
        return ids
    else:
        return []

# doc:   current model document
def GetAllUnUsedDetailSymbolIds(doc):
    '''get all unused detail symbol type ids in model'''
    ids = []
    allAvailableIds = GetAllDetailSymbolIdsAvailable(doc)
    allUsedIds = GetAllUsedDetailSymbolIds(doc)
    for id in allAvailableIds:
        if(id not in allUsedIds):
            ids.append(id)
    return ids

# doc:   current model document
def GetAllUnUsedDetailSymbolIdsForPurge(doc):
    '''get all unused detail symbol type ids in model to be purged (leaves one behind)'''
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetAllUnUsedDetailSymbolIds)
    return ids
    #ids = GetAllUnUsedDetailSymbolIds(doc)
    #allAvailableIds = GetAllDetailSymbolIdsAvailable(doc)
    # need to keep at least one
    #if(len(allAvailableIds) == len(ids)):
    #    ids.pop(0)
    #return ids

# -------------------------------- filled region types -------------------------------------------------------

# doc   current document
def GetAllFilledRegionTypeIdsAvailable(doc):
    '''get all filled regions types in model'''
    dic = BuildDetailTypeIdsDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(FILLED_REGION_TYPE)):
        return dic[FILLED_REGION_TYPE]
    else:
        return []

# doc   current document
def GetUsedFilledRegionTypeIds(doc):
    '''get all used filled regions types in model'''
    ids = []
    idsAll = GetAllFilledRegionTypeIdsAvailable(doc)
    for id in idsAll:
        el = doc.GetElement(id)
        dic = BuildDependentElementsDictionary(doc, el.GetDependentElements(None))
        if(dic.has_key('Autodesk.Revit.DB.FilledRegion')):
            ids.append(id)
    return ids

# doc   current document
def GetUnUsedFilledRegionTypeIds(doc):
    '''get all un used filled regions types in model'''
    ids = []
    idsAll = GetAllFilledRegionTypeIdsAvailable(doc)
    for id in idsAll:
        el = doc.GetElement(id)
        dic = BuildDependentElementsDictionary(doc, el.GetDependentElements(None))
        if(dic.has_key('Autodesk.Revit.DB.FilledRegion') == False):
            ids.append(id)
    return ids

# doc   current document
def GetUnUsedFilledRegionTypeIdsForPurge(doc):
    '''get all un used filled regions types in model'''
    ids = GetUnUsedFilledRegionTypeIds(doc)
    idsAll = GetAllFilledRegionTypeIdsAvailable(doc)
    # need to keep at least one
    if(len(idsAll) == len(ids)):
        ids.pop(0)
    return ids