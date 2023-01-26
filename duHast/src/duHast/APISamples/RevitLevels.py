'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit levels helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitWorksets as rWork
from duHast.APISamples import RevitFamilyUtils as rFamU
from duHast.APISamples import Result as res
from duHast.APISamples import Utility as util

# import Autodesk
import Autodesk.Revit.DB as rdb

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_LEVELS_HEADER = ['HOSTFILE', 'ID', 'NAME', 'WORKSETNAME', 'ELEVATION']

# --------------------------------------------- utility functions ------------------

def GetLevelsListAscending(doc):
    '''
    Gets a filtered element collector of all levels in the model ascending by project elevation.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of levels
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToList().OrderBy(lambda l: l.ProjectElevation)
    return collector

# ------------------------------------------------------- Level reporting --------------------------------------------------------------------

def GetLevelReportData(doc, revitFilePath):
    '''
    Gets level data ready for being printed to file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The file hostname, which is added to data returned.
    :type revitFilePath: str

    :return: list of list of revit level properties.
    :rtype: list of list of str
    '''

    data = []
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.Level):
        data.append([
            util.GetFileNameWithoutExt(revitFilePath), 
            str(p.Id.IntegerValue), 
            util.EncodeAscii(p.Name), 
            util.EncodeAscii(rWork.GetWorksetNameById(doc, p.WorksetId.IntegerValue)), 
            str(p.Elevation)])
    return data

# ------------------------------------------------- filters --------------------------------------------------------------------

def GetAllLevelHeadsByCategory(doc):
    '''
    Gets a filtered element collector of all level head types in the model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of level heads
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_LevelHeads).WhereElementIsElementType()
    return collector

def GetAllLevelTypesByCategory(doc):
    '''
    Gets a filtered element collector of all level types in the model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of level types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Levels).WhereElementIsElementType()
    return collector

def GetAllLevelTypeIdsByCategory(doc):
    '''
    Gets a list of all level type ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of all level type ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Levels).WhereElementIsElementType()
    ids = com.GetIdsFromElementCollector(collector)
    return ids

# -------------------------------------------------  purge --------------------------------------------------------------------

def GetUnusedLevelTypesForPurge(doc):
    '''
    Gets all ids of unused level types in the model.

    Unused: not one instance per level type is placed in the model.
    This method can be used to safely delete unused level types from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of level type ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    return com.GetUsedUnusedTypeIds(doc, GetAllLevelTypeIdsByCategory, 0, 6)

def GetUnusedLevelHeadFamilies(doc):
    '''
    Gets all ids of unused family symbols (types) of level head families.

    Unused: not one instance per symbol is placed in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of symbol ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    usedTypes = com.GetUsedUnusedTypeIds(doc, GetAllLevelTypeIdsByCategory, 1, 6)
    headsInUseIds = []
    # get family symbol in use at level as symbol
    for lId in usedTypes:
        type = doc.GetElement(lId)
        id = com.GetBuiltInParameterValue(type, rdb.BuiltInParameter.LEVEL_HEAD_TAG)
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

def GetAllLevelHeadFamilyTypeIds(doc):
    '''
    Gets ids of all level head family symbols (types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of symbol ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_LevelHeads)
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(filter)
    ids = com.GetIdsFromElementCollector(col)
    return ids

# doc             current document
def GetUnusedLevelHeadFamiliesForPurge(doc):
    '''
    Gets ids of all unused level head symbols and families.

    Unused: not one instance per level symbol is placed in the model.
    This method can be used to safely delete unused level symbols or families from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: A list of symbol and or family ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    return rFamU.GetUnusedInPlaceIdsForPurge(doc, GetUnusedLevelHeadFamilies)