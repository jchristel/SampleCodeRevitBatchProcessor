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
import Result as res
import Utility as util

# import Autodesk
from Autodesk.Revit.DB import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_GROUPS_HEADER = ['HOSTFILE','ID', 'ITEM TYPE']

# --------------------------------------------- utility functions ------------------

# returns a list of filled region elements from the model
# doc   current document
def GetFilledRegionsInModel(doc):
    return FilteredElementCollector(doc).OfClass(FilledRegion).ToList()


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
    """ this will return a filtered element collector of all detail component types in the model"""
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DetailComponents).WhereElementIsElementType()
    return collector

# collector   filtered element collector detail component types
def BuildDetailTypesDictionary(collector):
    """returns the dictionary keys is autodesk.revit.db element type as string and values are available types"""
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
    """returns the dictionary keys is autodesk.revit.db element type as string and values are elements"""
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
def GetAllRepeatingDetailTypesAvailable(doc):
    """get all repeating detail types in model"""
    dic = BuildDetailTypesDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(ELEMENT_TYPE)):
        return dic[ELEMENT_TYPE]
    else:
        return []

# doc   current document
def GetUsedRepeatingDetailTypeIds(doc):
    """get all used repeating detail type ids"""
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRepeatingDetailTypesAvailable, 1, 1)
    return ids

# doc   current document
def GetUnUsedRepeatingDetailTypeIds(doc):
    """get all unused repeating detail type ids"""
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRepeatingDetailTypesAvailable, 0, 1)
    return ids

# doc   current document
def GetUnUsedRepeatingDetailTypeIdsForPurge(doc):
    """get all unused repeating detail type ids"""
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRepeatingDetailTypesAvailable, 0, 1)
    allIds = GetAllRepeatingDetailTypesAvailable(doc)
    # need to keep at least one
    if(len(allIds) == len(ids)):
        ids.pop(0)
    return ids
# -------------------------------- filled region types -------------------------------------------------------

# doc   current document
def GetAllFilledRegionTypesAvailable(doc):
    """get all filled regions types in model"""
    dic = BuildDetailTypesDictionary(GetAllDetailTypesByCategory(doc))
    if (dic.has_key(FILLED_REGION_TYPE)):
        return dic[FILLED_REGION_TYPE]
    else:
        return []

# doc   current document
def GetUsedFilledRegionTypeIds(doc):
    """get all used filled regions types in model"""
    ids = []
    idsAll = GetAllFilledRegionTypesAvailable(doc)
    for id in idsAll:
        el = doc.GetElement(id)
        dic = BuildDependentElementsDictionary(doc, el.GetDependentElements(None))
        if(dic.has_key(FILLED_REGION_TYPE)):
            ids.append(id)
    return ids

# doc   current document
def GetUnUsedFilledRegionTypeIds(doc):
    """get all un used filled regions types in model"""
    ids = []
    idsAll = GetAllFilledRegionTypesAvailable(doc)
    for id in idsAll:
        el = doc.GetElement(id)
        dic = BuildDependentElementsDictionary(doc, el.GetDependentElements(None))
        if(dic.has_key(FILLED_REGION_TYPE) == False):
            ids.append(id)
    return ids

# doc   current document
def GetUnUsedFilledRegionTypeIdsForPurge(doc):
    """get all un used filled regions types in model"""
    ids = []
    idsAll = GetAllFilledRegionTypesAvailable(doc)
    for id in idsAll:
        el = doc.GetElement(id)
        dic = BuildDependentElementsDictionary(doc, el.GetDependentElements(None))
        if(dic.has_key('Autodesk.Revit.DB.FilledRegion') == False):
            ids.append(id)
    # need to keep at least one
    if(len(idsAll) == len(ids)):
        ids.pop(0)
    return ids