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

# doc:   current model document
def GetLevelsListAscending(doc):
    ''' this will return a filtered element collector of all levels in the model ascending by project elevation'''
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToList().OrderBy(lambda l: l.ProjectElevation)
    return collector

# ------------------------------------------------------- Level reporting --------------------------------------------------------------------

# gets level data ready for being printed to file
# doc: the current revit document
# revitFilePath: fully qualified file path of Revit file
def GetLevelReportData(doc, revitFilePath):
    data = []
    for p in FilteredElementCollector(doc).OfClass(Level):
        data.append([
            util.GetFileNameWithoutExt(revitFilePath), 
            str(p.Id.IntegerValue), 
            util.EncodeAscii(p.Name), 
            util.EncodeAscii(rWork.GetWorksetNameById(doc, p.WorksetId.IntegerValue)), 
            str(p.Elevation)])
    return data

# ------------------------------------------------- filters --------------------------------------------------------------------

# doc:   current model document
def GetAllLevelHeadsByCategory(doc):
    ''' this will return a filtered element collector of all level head types in the model'''
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_LevelHeads).WhereElementIsElementType()
    return collector

# doc:   current model document
def GetAllLevelTypesByCategory(doc):
    ''' this will return a filtered element collector of all level types in the model'''
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsElementType()
    return collector

# doc:   current model document
def GetAllLevelTypeIdsByCategory(doc):
    ''' this will return a filtered element collector of all level type ids in the model'''
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(collector)
    return ids

# -------------------------------------------------  purge --------------------------------------------------------------------

# doc             current document
def GetUnusedLevelTypesForPurge(doc):
    ''' this will return all ids of unused level types in the model to be purged'''
    return com.GetUsedUnusedTypeIds(doc, GetAllLevelTypeIdsByCategory, 0, 6)

# doc             current document
def GetUnusedLevelHeadFamilies(doc):
    ''' this will return all ids of unused family symbols (types) of level head families'''
    usedTypes = com.GetUsedUnusedTypeIds(doc, GetAllLevelTypeIdsByCategory, 1, 6)
    headsInUseIds = []
    # get family symbol in use at level as symbol
    for lId in usedTypes:
        type = doc.GetElement(lId)
        id = com.GetBuiltInParameterValue(type, BuiltInParameter.LEVEL_HEAD_TAG)
        if(id != None and id not in headsInUseIds):
            headsInUseIds.append(id)
    # get all level head symbols available
    allSymbolsInModel = GetAllLevelHeadsByCategory(doc)
    unusedSymbolIds = []
    # filter out unused level head symbols and add to list to be returned
    for  levelSymbolInModel in  allSymbolsInModel:
        if(levelSymbolInModel.Id not in headsInUseIds ):
            unusedSymbolIds.append(levelSymbolInModel.Id)
    return unusedSymbolIds

# doc             current document
def GetAllLevelHeadfamilyTypeIds(doc):
    ''' this will return all ids level head family types in the model'''
    ids = []
    filter = ElementCategoryFilter(BuiltInCategory.OST_LevelHeads)
    col = FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(filter)
    ids = com.GetIdsFromElementCollector(col)
    return ids

# doc             current document
def GetUnusedLevelHeadFamiliesForPurge(doc):
    ''' this will return all ids of unused level head symbols and families to be purged'''
    return rFamU.GetUnusedInPlaceIdsForPurge(doc, GetUnusedLevelHeadFamilies)