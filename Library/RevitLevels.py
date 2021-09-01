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
import RevitWorksets as rWork
import RevitFamilyUtils as rFamU
import Result as res
import Utility as util

# import Autodesk
from Autodesk.Revit.DB import *

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
# header used in reports
REPORT_LEVELS_HEADER = ['HOSTFILE', 'ID', 'NAME', 'WORKSETNAME', 'ELEVATION']

# --------------------------------------------- utility functions ------------------

# ------------------------------------------------------- Level reporting --------------------------------------------------------------------

# gets level data ready for being printed to file
# doc: the current revit document
# revitFilePath: fully qualified file path of Revit file
def GetLevelReportData(doc, revitFilePath):
    data = []
    for p in FilteredElementCollector(doc).OfClass(Level):
        data.append('\t'.join([
            util.GetFileNameWithoutExt(revitFilePath), 
            str(p.Id.IntegerValue), 
            util.EncodeAscii(p.Name), 
            rWork.GetWorksetNameById(doc, p.WorksetId.IntegerValue), 
            str(p.Elevation)]))
    return data

# ------------------------------------------------- filters --------------------------------------------------------------------

# returns all wall level head family symbols in a model
# doc:   current model document
def GetAllLevelHeadsByCategory(doc):
    """ this will return a filtered element collector of all level head types in the model"""
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_LevelHeads).WhereElementIsElementType()
    return collector

# returns all level types in a model
# doc:   current model document
def GetAllLevelTypesByCategory(doc):
    """ this will return a filtered element collector of all level types in the model"""
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsElementType()
    return collector

# returns all level types in a model
# doc:   current model document
def GetAllLevelTypeIdsByCategory(doc):
    """ this will return a filtered element collector of all level type ids in the model"""
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(collector)
    return ids


# -------------------------------------------------  purge --------------------------------------------------------------------

# doc             current document
# useTyep         0, no dependent elements; 1: has dependent elements
# typeIdGetter    list of type ids to be checked for dependent elements
def GetUsedUnusedTypeIds(doc, typeIdGetter, useType = 0):
    # get all types elements available
    allTypeIds = typeIdGetter(doc)
    ids = []
    for typeId in allTypeIds:
        type = doc.GetElement(typeId)
        hasDependents = com.HasDependentElements(doc, type, None, 6)
        if(hasDependents == useType):
            ids.append(typeId)
    return ids

# doc             current document
def GetUnusedLevelTypesForPurge(doc):
    """ this will return all ids of unused level types in the model to be purged"""
    return GetUsedUnusedTypeIds(doc, GetAllLevelTypeIdsByCategory, 0)

# doc             current document
def GetUnusedLevelHeadFamilies(doc):
    """ this will return all ids of unused family symbols (types) of level head families"""
    usedLevelTypes = GetUsedUnusedTypeIds(doc, GetAllLevelTypeIdsByCategory, 1)
    headsInUseIds = []
    # get family symbol in use at level as symbol
    for lId in usedLevelTypes:
        levelType = doc.GetElement(lId)
        paras = levelType.GetOrderedParameters()
        for p in paras:
            if(p.Definition.BuiltInParameter == BuiltInParameter.LEVEL_HEAD_TAG):
                if (com.getParameterValue(p) not in headsInUseIds):
                    headsInUseIds.append(com.getParameterValue(p))
                break
    # get all level head symbols available
    allLevelSymbolsInModel = GetAllLevelHeadsByCategory(doc)
    unusedLevelSymbolIds = []
    # filter out unused level head symbols and add to list to be returned
    for  levelSymbolInModel in  allLevelSymbolsInModel:
        if(levelSymbolInModel.Id not in headsInUseIds ):
            unusedLevelSymbolIds.append(levelSymbolInModel.Id)
    return unusedLevelSymbolIds

# doc             current document
def GetUnusedLevelHeadFamiliesForPurge(doc):
    """ this will return all ids of unused level head symbols and families to be purged"""
    return rFamU.GetUnusedInPlaceIdsForPurge(doc, GetUnusedLevelHeadFamilies)