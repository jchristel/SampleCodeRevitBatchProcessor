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
from System.Collections.Generic import List

import RevitCommonAPI as com
import RevitFamilyUtils as rFam

# import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_RailingS_HEADER = ['HOSTFILE', 'RAILINGTYPEID', 'RAILINGTYPENAME']

RAILING_FAMILY_NAME = 'Railing'
TOP_RAIL_FAMILY_NAME = 'Top Rail Type'
HAND_RAIL_FAMILY_NAME = 'Handrail Type'

BUILTIN_RAILING_TYPE_FAMILY_NAMES = [
    RAILING_FAMILY_NAME,
    TOP_RAIL_FAMILY_NAME,
    HAND_RAIL_FAMILY_NAME
]

# category filter for all element filters by category
RAILING_CATEGORYFILTER = List[BuiltInCategory] ([
        BuiltInCategory.OST_Railings,
        BuiltInCategory.OST_RailingBalusterRail,
        BuiltInCategory.OST_RailingHandRail,
        BuiltInCategory.OST_RailingSupport,
        BuiltInCategory.OST_RailingSystem,
        BuiltInCategory.OST_RailingTermination,
        BuiltInCategory.OST_RailingTopRail,
    ])

# --------------------------------------------- utility functions ------------------

# doc:   current model document
def GetAllRailingTypesByCategory(doc):
    """ this will return a filtered element collector of all Railing types in the model:
    - Top Rail
    - support
    - hand rail
    - In place families or loaded families
    it will therefore not return any Rail types ..
    """
    multiCatFilter = ElementMulticategoryFilter(RAILING_CATEGORYFILTER)
    collector = FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsElementType()
    return collector

# doc:   current model document
def GetAllRailingTypesByCategoryExclInPlace(doc):
    """ this will return a filtered element collector of all Railing types in the model:
    - Top Rail
    - support
    - hand rail
    it will therefore not return any Rail types ..
    """
    multiCatFilter = ElementMulticategoryFilter(RAILING_CATEGORYFILTER)
    collector = FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsElementType()
    elements=[]
    for c in collector:
        if(c.GetType() != FamilySymbol):
            elements.append(c)
    return elements
    
# doc   current model document
def GetRailingTypesByClass(doc):
    """ this will return a filtered element collector of all Railing types in the model:
    - Railing
    it will therefore not return any top rail or hand rail or in place family types ..."""
    return  FilteredElementCollector(doc).OfClass(RailingType)

# collector   fltered element collector containing Railing type elments of family symbols representing in place families
# dic         dictionary containing key: rail type family name, value: list of ids
def BuildRailingTypeDictionary(collector, dic):
    """returns the dictioanry passt in with keys and or values added retrieved from collector passt in"""
    for c in collector:
        if(dic.has_key(c.FamilyName)):
            if(c.Id not in dic[c.FamilyName]):
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic

# doc   current model document
def SortRailingTypesByFamilyName(doc):
    # get all Railing Type Elements
    wts = GetRailingTypesByClass(doc)
    # get all Railing types including in place railing families
    wts_two = GetAllRailingTypesByCategory(doc)
    usedWts = {}
    usedWts = BuildRailingTypeDictionary(wts, usedWts)
    usedWts = BuildRailingTypeDictionary(wts_two, usedWts)
    return usedWts

# -------------------------------- none in place Railing types -------------------------------------------------------

# doc   current model document
def GetAllRailingInstancesInModelByCategory(doc):
    """ returns all Railing elements placed in model...ignores in foundation slabs"""
    multiCatFilter = ElementMulticategoryFilter(RAILING_CATEGORYFILTER)
    return FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsNotElementType()
    
# doc   current model document
def GetAllRailingInstancesInModelByClass(doc):
    """ returns all Railing elements placed in model...ignores in place"""
    return FilteredElementCollector(doc).OfClass(Railing).WhereElementIsNotElementType()

# doc   current model document
def GetAllRailingTypeIdsInModelByCategory(doc):
    """ returns all Railing element types available in model """
    ids = []
    colCat = GetAllRailingTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector (colCat)
    return ids

# doc   current model document
def GetAllRailingTypeIdsInModelByClass(doc):
    """ returns all Railing element types available in model """
    ids = []
    colClass = GetRailingTypesByClass(doc)
    ids = com.GetIdsFromElementCollector(colClass)
    return ids

# doc   current model document
def GetAllRailingTypeIdsInModelByClassAndCategory(doc):
    """ returns all Railing element types available in model excluding in place types"""
    ids = []
    colClass = GetRailingTypesByClass(doc)
    idsClass = com.GetIdsFromElementCollector(colClass)
    colCat = GetAllRailingTypesByCategoryExclInPlace(doc)
    idsCat = com.GetIdsFromElementCollector(colCat)
    for idsc in idsClass:
        if (idsc not in ids):
            ids.append (idsc)
    for idsca in idsCat:
        if( idsca not in ids):
            ids.append(idsca)
    return ids

# doc   current document
def GetUsedRailingTypeIds(doc):
    """ returns all used in Railing type ids """
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRailingTypeIdsInModelByClassAndCategory, 1)
    return ids

# famTypeIds        symbol(type) ids of a family
# usedTypeIds       symbol(type) ids in use in a project
def FamilyNoTypesInUse(famTypeIds,unUsedTypeIds):
    """ returns false if any symbols (types) of a family are in use in a model"""
    match = True
    for famTypeId in famTypeIds:
        if (famTypeId not in unUsedTypeIds):
            match = False
            break
    return match
 
# doc   current document
def GetUnusedNonInPlaceRailingTypeIdsToPurge(doc):
    """ returns all unused Railing type ids for:
    - Railing
    - Hand rail
    - Top Rail
    it will therefore not return any in place family types ..."""
    # get unused type ids
    ids = com.GetUsedUnusedTypeIds(doc, GetAllRailingTypeIdsInModelByClassAndCategory, 0)
    # make sure there is at least on Railing type per system family left in model
    RailingTypes = SortRailingTypesByFamilyName(doc)
    for key, value in RailingTypes.items():
        if(key in BUILTIN_RAILING_TYPE_FAMILY_NAMES):
            if(FamilyNoTypesInUse(value,ids) == True):
                # remove one type of this system family from unused list
                ids.remove(value[0])
    return ids
 
# -------------------------------- In place Railing types -------------------------------------------------------

# doc   current document
def GetInPlaceRailingFamilyInstances(doc):
    """ returns all instances in place families of category Railing"""
    # built in parameter containing family name when filtering familyInstance elements:
    # BuiltInParameter.ELEM_FAMILY_PARAM
    # this is a faster filter in terms of performance then LINQ query refer to:
    # https://jeremytammik.github.io/tbc/a/1382_filter_shortcuts.html
    filter = ElementMulticategoryFilter(RAILING_CATEGORYFILTER)
    return FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(filter)

# doc   current document
def GetAllInPlaceRailingTypeIdsInModel(doc):
    """ returns type ids off all available in place families of category Railing"""
    ids = []
    for cat in RAILING_CATEGORYFILTER: 
        idsByCat = rFam.GetAllInPlaceTypeIdsInModelOfCategory(doc, cat)
        if(len(idsByCat) > 0):
            ids = ids + idsByCat
    return ids

# doc   current document
def GetUsedInPlaceRailingTypeIds(doc):
    """ returns all used in place type ids """
    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceRailingTypeIdsInModel, 1)
    return ids

# doc   current document
def GetUnusedInPlaceRailingTypeIds(doc):
    """ returns all unused in place type ids """
    ids = com.GetUsedUnusedTypeIds(doc, GetAllInPlaceRailingTypeIdsInModel, 0)
    return ids

# doc   current document
def GetUnusedInPlaceRailingIdsForPurge(doc):
    """returns symbol(type) ids and family ids (when no type is in use) of in place Railing familis which can be purged"""
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnusedInPlaceRailingTypeIds)
    return ids


# -------------------------------- baluster types -------------------------------------------------------
# -------------baluster utility -------------

# listSource    list to be added to
# listMerge     list containing new values to be added to listSource
def MergeIntoUniquList(listSource, listMerge):
    '''merges the second list into the first by adding elements from second list which are not already in first list'''
    for i in listMerge:
        if (i not in listSource):
            listSource.append(i)
    return listSource

# bPostPattern    baluster pattern element
def GetBalustersUsedInPattern(bpattern):
    '''return list of unique baluster ids used in a pattern only'''
    ids = []
    for i in range(0, bpattern.GetBalusterCount()):
        balInfo = bpattern.GetBaluster(i)
        if(balInfo.BalusterFamilyId not in ids and balInfo.BalusterFamilyId != ElementId.InvalidElementId ):
            ids.append(balInfo.BalusterFamilyId)
    # add excess pattern baluster id
    if (bpattern.ExcessLengthFillBalusterId not in ids and bpattern.ExcessLengthFillBalusterId != ElementId.InvalidElementId):
        ids.append(bpattern.ExcessLengthFillBalusterId)
    return ids

# bPostPattern    Post pattern element
def GetUsedBalusterPostIds(bPostPattern):
    '''return list of unique baluster posts ids only:
    - CornerPost
    - EndPost
    - StartPost
    '''
    ids = []
    # get corner post
    if(bPostPattern.CornerPost.BalusterFamilyId != ElementId.InvalidElementId):
        ids.append(bPostPattern.CornerPost.BalusterFamilyId)
    # get end post id
    if(bPostPattern.EndPost.BalusterFamilyId != ElementId.InvalidElementId and bPostPattern.EndPost.BalusterFamilyId not in ids):
        ids.append(bPostPattern.EndPost.BalusterFamilyId)
    # get start post id
    if(bPostPattern.StartPost.BalusterFamilyId != ElementId.InvalidElementId and bPostPattern.StartPost.BalusterFamilyId not in ids):
        ids.append(bPostPattern.StartPost.BalusterFamilyId)
    return ids

# bPlacement    baluster placement element
def GetUsedBalusterPerTread(bPlacement):
    ''' gets the id of the baluster per tread'''
    ids = []
    # get baluster per tread
    if(bPlacement.BalusterPerTreadFamilyId != ElementId.InvalidElementId):
        ids.append(bPlacement.BalusterPerTreadFamilyId)
    return ids

# -------------baluster utility end-------------

# doc   current document
def GetAllBalusterSymbols(doc):
    """ returns all baluster symbols in project"""
    col = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsRailingBaluster).WhereElementIsElementType()
    return col

 # doc   current document
def GetAllBalusterSymbolIds(doc):
    """ returns all baluster symbol ids in project"""
    ids = []
    col = GetAllBalusterSymbols(doc)
    ids = com.GetIdsFromElementCollector (col)
    return ids

# doc   current document
def GetBalusterTypesFromRailings(doc):
    '''returns a unique list of all baluster symbol type ids used in railing types in the model'''
    ids = []
    railingTypeIds = GetAllRailingTypeIdsInModelByClassAndCategory(doc)
    for rtId in railingTypeIds:
        el = doc.GetElement(rtId)
        # put into try catch since some rail types have no balusters ...top rail
        try:
            btplace = el.BalusterPlacement
            idsPattern = GetBalustersUsedInPattern(btplace.BalusterPattern)
            idsPosts = GetUsedBalusterPostIds(btplace.PostPattern)
            idsPerTread = GetUsedBalusterPerTread(btplace)
            # build overall ids list
            ids = MergeIntoUniquList(ids, idsPattern)
            ids = MergeIntoUniquList(ids, idsPosts)
            ids = MergeIntoUniquList(ids, idsPerTread)
        except:
            pass
    return ids

# doc   current document
def GetUsedBalusterTypeIds(doc):
    """ returns all used baluster type ids """
    ids = []
    idsUsedInModel = com.GetUsedUnusedTypeIds(doc, GetAllBalusterSymbolIds, 1)
    idsUsedInRailings = GetBalusterTypesFromRailings(doc)
    ids = MergeIntoUniquList(ids, idsUsedInModel)
    ids = MergeIntoUniquList(ids, idsUsedInRailings)
    return ids

# doc   current document
def GetUnUsedBalusterTypeIds(doc):
    """ returns all unused baluster type ids """
    ids = []
    idsUsed = GetUsedBalusterTypeIds(doc)
    idsAvailable = GetAllBalusterSymbolIds(doc)
    for id in idsAvailable:
        if (id not in idsUsed):
            ids.append(id)
    return ids

# doc   current document
def GetUnUsedBalusterTypeIdsForPurge(doc):
    """get all un used baluster type ids"""
    ids = rFam.GetUnusedInPlaceIdsForPurge(doc, GetUnUsedBalusterTypeIds)
    return ids
    # no need to keep anything...?
    #idsAll =  GetAllBalusterSymbolIds(doc)
    # need to keep at least one ( do I ...?)
    #if(len(idsAll) == len(ids)):
    #    ids.pop(0)
    return ids