'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit grids helper functions.
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
from duHast.APISamples import Result as res
from duHast.APISamples import Utility as util
from duHast.APISamples import RevitFamilyUtils as rFamU

# import Autodesk
import Autodesk.Revit.DB as rdb

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_GRIDS_HEADER = ['HOSTFILE','ID', 'NAME', 'WORKSETNAME', 'EXTENTMAX', 'EXTENTMIN']

# --------------------------------------------- utility functions ------------------

def GetAllGridHeadsByCategory(doc):
    '''
    Gets all grid head types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector with grid head types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_GridHeads).WhereElementIsElementType()
    return collector

def GetAllGridTypesByCategory(doc):
    '''
    Gets all grid types in the model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector with grid types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Grids).WhereElementIsElementType()
    return collector

def GetAllGridTypeIdsByCategory(doc):
    '''
    Gets all grid types ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector with grid type ids
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = GetAllGridTypesByCategory(doc)
    ids = com.GetIdsFromElementCollector(collector)
    return ids

def GetGridTypeNames (doc, g):
    '''
    Gets all valid grid types, based on a past in grid, available in model.

    Uses grid.GetValidTypes() to get the grid types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param g: A grid
    :type g: Autodesk.Revit.DB.Grid
    :return: A nested set of lists containing grid type id and grid type name
    :rtype: list of lists [[GridTypeId as Revit ElementId, grid type name as string],[...]]
    '''

    validGridTypes = []
    validGridTypeIds = g.GetValidTypes()
    for validGridTypeId in validGridTypeIds:
        gridData = []
        gtypeT = doc.GetElement(validGridTypeId)
        gridData.append(validGridTypeId)
        gridData.append(rdb.Element.Name.GetValue(gtypeT))
        validGridTypes.append(gridData)
    return validGridTypes

def GetGridTypeName (doc, g):
    '''
    Gets the grid type name of a grid.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param g: A grid.
    :type g: Autodesk.Revit.DB.Grid
    :return: The grid type name.
    :rtype: str
    '''

    value = 'unknown'
    gtypeT = doc.GetElement(g.GetTypeId())
    value = rdb.Element.Name.GetValue(gtypeT)
    return value

def GetGridTypeIdByName (doc, gridTypeName):
    '''
    Gets the grid type Id based on it's name, if no match found it returns the Revit Invalid Element Id

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param gridTypeName: The grid type name.
    :type gridTypeName: str
    :return: The grids type Id or if not match is found Autodesk.Revit.DB.ElementId.InvalidElementId
    :rtype: Autodesk.Revit.DB.ElementId
    '''

    id = rdb.ElementId.InvalidElementId
    grids = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid).ToList()
    if(len(grids) > 0):
        g = grids[0]
        validGridTypeIds = g.GetValidTypes()
        for gridTypId in validGridTypeIds:
            gtypeTName = rdb.Element.Name.GetValue(doc.GetElement(gridTypId))
            if(gtypeTName ==  gridTypeName):
                id = gridTypId
                break
    return id

def GridCheckParameterValue(g, paraName, paraCondition, conditionValue):
    '''
    Returns true if a given parameter on a grid has a value meeting the parameter condition.

    :param g: A grid.
    :type g: Autodesk.Revit.DB.Grid
    :param paraName: A parameter Name.
    :type paraName: str
    :param paraCondition: A function evaluating the parameter value. First argument is the value to be checked against. Second argument is the actual parameter value.
    :type paraCondition: func(arg1,arg2)
    :param conditionValue: The value to be checked against.
    :type conditionValue: var
    :return: True if parameter value is evaluated to True otherwise False.
    :rtype: bool
    '''
    ruleMatch = False
    pValue = com.GetParameterValueByName(g, paraName)
    if (pValue != None):
        ruleMatch = com.CheckParameterValue(g, paraCondition, conditionValue)
    return ruleMatch

def GetMaxExtentAsString(g):
    '''
    Gets the maximum extent of a grid.

    :param g: A grid.
    :type g: Autodesk.Revit.DB.Grid
    :return: A string in format [maxX,maxY,maxZ]<tab>[minX,minY,minZ]
    :rtype: str
    '''

    ex = g.GetExtents()
    max = '['+ ','.join([str(ex.MaximumPoint.X), str(ex.MaximumPoint.Y), str(ex.MaximumPoint.Z)]) + ']'
    min = '['+ ','.join([str(ex.MinimumPoint.X), str(ex.MinimumPoint.Y), str(ex.MinimumPoint.Z)]) + ']'    
    return '\t'.join([min, max])

# ------------------------------------------------------ grids workset modifiers ------------------------------------------
# workset modifier method
# moves all grids to one workset
# returns a result object
# rules format:
#['Model name',[
#       [workset modifier method,
#           [worksetName]
#           ]
#       ]
def ModifyGridWorkSetsDefault (doc, worksetRules):
    gridsResults = res.Result()
    collectorGrids = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid)
    for rule in worksetRules:
        for defaultWorksetName in rule:
            grids = rWork.ModifyElementWorkset(doc, defaultWorksetName, collectorGrids, 'grids')
            gridsResults.Update(grids)
    return gridsResults

# workset modifier method
# moves grids matching type condition to a particular workset
# returns a result object
#defaultWorksetTypeRules_ = [
#    ['model name',[
#        [ModifyGridWorkSetsByTypeName,[
#            ['workset name', util.ConDoesNotEqual, 'grid type name'],
#            ['workset name', util.ConDoesEqual, 'grid type name']
#            ]
#        ]
#        ]
#    ]
#]
def ModifyGridWorkSetsByTypeName(doc, worksetRules):
    gridsResults = res.Result()
    # loop over grid type filter and address one at the time
    # get all grids matching type name filter
    for defaultWorksetName, typeNameCondition, typeName,  in worksetRules:
        # get the grid type id from the type name
        typeId = GetGridTypeIdByName(doc, typeName)
        collectorGrids = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid).Where(lambda e: typeNameCondition(e.GetTypeId(), typeId))
        grids = rWork.ModifyElementWorkset(doc, defaultWorksetName, collectorGrids, 'grids')
        gridsResults.Update(grids)
    return gridsResults

# workset modifier method
# moves grids matching parameter condition to a particular workset
# returns a result object
#defaultWorksetRulesNames_ = [
#    ['model name',[
#        [ModifyGridWorkSetsByParameterValue,[
#            ['workset name', util.ConTwoStartWithOne, 'Name' ,'name starts with value']
#            ]
#        ]
#        ]
#    ]
#]
def ModifyGridWorkSetsByParameterValue(doc, worksetRules):
    gridsResults = res.Result()
    # loop over grid parameter filter and address one at the time
    # get all grids matching filter
    for defaultWorksetName, paraCondition, paraName, conditionValue  in worksetRules:
        collectorGrids = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid).Where(lambda e: GridCheckParameterValue(e, paraName, paraCondition, conditionValue))
        grids = rWork.ModifyElementWorkset(doc, defaultWorksetName, collectorGrids, 'grids')
        gridsResults.Update(grids)
    return gridsResults

# modifies worksets of grids as per workset rules
# returns a result object
# doc: the current revit document
# rules format:
#defaultWorksetRulesAll_ = [
#    ['model name',[
#        [ModifyGridWorkSetsDefault,[
#            ['default workset name'] # there should only be one per model
#            ]
#        ]
#        ]
#    ]
#]
def ModifyGridsWorksets(doc, revitFileName, worksetRules):
    gridsResults = res.Result()
    foundMatch = False
    for fileName, worksetModifierList in worksetRules:
        if (revitFileName.startswith(fileName)):
            foundMatch = True
            for worksetModifier, rules in worksetModifierList:
                grids = worksetModifier(doc, rules)
                gridsResults.Update(grids)
            break
    if foundMatch == False:
        gridsResults.UpdateSep(False, 'No grid rules found for file: ' + revitFileName)
    return gridsResults

# ------------------------------------------------------- Grid reporting --------------------------------------------------------------------

def GetGridReportData(doc, revitFilePath):
    '''
    Gets grid data ready for being printed to file

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: fully qualified file path of Revit file
    :type revitFilePath: str

    :return: list of list of revit grid properties.
    :rtype: [[str]]
    '''

    data = []
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.Grid):
        data.append([
            util.GetFileNameWithoutExt(revitFilePath), 
            str(p.Id.IntegerValue), 
            util.EncodeAscii(p.Name), 
            rWork.GetWorksetNameById(doc, p.WorksetId.IntegerValue), 
            GetMaxExtentAsString(p)])
    return data

# -------------------------------------------------  purge --------------------------------------------------------------------

# doc             current document
def GetUnusedGridTypesForPurge(doc):
    ''' this will return all ids of unused grid types in the model to be purged'''
    return com.GetUsedUnusedTypeIds(doc, GetAllGridTypeIdsByCategory, 0, 8)

# doc             current document
def GetAllGridHeadFamilyTypeIds(doc):
    ''' this will return all ids grid head family types in the model'''
    ids = []
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_GridHeads)
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(filter)
    ids = com.GetIdsFromElementCollector(col)
    return ids

# doc             current document
def GetUnusedGridHeadFamilies(doc):
    ''' this will return all ids of unused family symbols (types) of grid head families'''
    usedTypes = com.GetUsedUnusedTypeIds(doc, GetAllGridTypeIdsByCategory, 1, 8)
    headsInUseIds = []
    for Id in usedTypes:
        type = doc.GetElement(Id)
        id = com.GetBuiltInParameterValue(type, rdb.BuiltInParameter.GRID_HEAD_TAG)
        if (id != None and id not in headsInUseIds):
            headsInUseIds.append(id)
    allSymbolsInModel = GetAllGridHeadsByCategory(doc)
    unusedSymbolIds = []
    for  symbolInModel in  allSymbolsInModel:
        if(symbolInModel.Id not in headsInUseIds ):
            unusedSymbolIds.append(symbolInModel.Id)
    return unusedSymbolIds 

# doc             current document
def GetUnusedGridHeadFamiliesForPurge(doc):
    ''' this will return all ids of unused grid head symbols and families to be purged'''
    return rFamU.GetUnusedInPlaceIdsForPurge(doc, GetUnusedGridHeadFamilies)