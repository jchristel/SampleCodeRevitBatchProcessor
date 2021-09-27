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

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)
clr.AddReference('System')

import Utility as util
import RevitBIM360 as b360
import RevitCommonAPI as com
import Result as res
import RevitDesignSetOptions as rDoS
import RevitWarnings as rWarn
import RevitWorksets as rWork
import RevitViews as rViews
import RevitLineStylesPatterns as rLsp
import RevitLinks as rLinks
import RevitModelHealthReportFileNames as rFns
import RevitFamilyUtils as rFams
import RevitGroups as rGrp
import RevitRooms as rRooms
import RevitDetailItems as rDetItems

from Autodesk.Revit.DB import *
from System.Collections.Generic import List
from collections import namedtuple

# constants
# health tracer family name
MODEL_HEALTH_TRACKER_FAMILY = 'Symbol_GraphicModelHealth_ANN'
# default value if unable to retrieve value from model
FAILED_TO_RETRIEVE_VALUE = -1

# doc   current document
def GetInstancesOfModelHealth(doc):
    """gets all instances of the model health tracker family in a model"""
    # built in parameter containing family name when filtering familyInstance elements:
    # BuiltInParameter.ELEM_FAMILY_PARAM
    # this is a faster filter in terms of performance then LINQ query refer to:
    # https://jeremytammik.github.io/tbc/a/1382_filter_shortcuts.html
    provider = ParameterValueProvider(ElementId(BuiltInParameter.ELEM_FAMILY_PARAM))
    evaluator = FilterStringEquals()
    rule = FilterStringRule( provider, evaluator, MODEL_HEALTH_TRACKER_FAMILY, True )
    filter = ElementParameterFilter( rule )
    return FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(filter).ToList()

# famInstance   an instance of the family model health tracker
# doc           current document
def GetParametersOfInstance(famInstance, doc):
    """update parameter values of model tracker family instance"""
    resultValue = res.Result()
    flagUpdate = False
    for p in famInstance.GetOrderedParameters():
        # check if parameter is read only
        if(p.IsReadOnly == False):
            # check an action to update this parameter value exists
            if(PARAM_ACTIONS.ContainsKey(p.Definition.Name)):
                pvalue = PARAM_ACTIONS[p.Definition.Name].getData(doc)
                if(pvalue != FAILED_TO_RETRIEVE_VALUE):
                    flag = com.setParameterValue(p, str(pvalue), doc)
                    resultValue.Update(flag)
                    flagUpdate = True
                else:
                    resultValue.UpdateSep(False, 'Failed to get value for ' + p.Definition.Name)
    if(flagUpdate == False):
        resultValue.message = 'No family parameters where updated'
        resultValue.status = True
    return resultValue

# ----------------------------------------------
# model properties 
# ----------------------------------------------

# --------------------------------------------- GENERAL ---------------------------------------------

# number of worksets in model
# doc   current document
def GetWorksetNumber(doc):
    return len(rWork.GetWorksets(doc))

# get the file size in MB
# doc   current document
def GetFileSize(doc):
    size = FAILED_TO_RETRIEVE_VALUE
    try:
        # get the path from the document
        # this will fail if not a file based doc or the document is detached
        revitFilePath = doc.PathName
        # check if bim 360 file
        if (revitFilePath.StartsWith('BIM 360')):
            size = b360.GetModelFileSize(doc)
        else:
            if(util.FileExist(revitFilePath)):
                # get file size in MB
                size = util.GetFileSize(revitFilePath)
    except:
        pass
    return size

# number of warnings in a model
# doc   current document
def GetNumberOfWarnings(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rWarn.GetWarnings(doc))
    except:
        pass
    return number
    
# returns the number of design sets in a model
# doc   current document
def GetNumberOfDesignSets(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rDoS.GetDesignSets(doc))
    except:
        pass
    return number

# returns the number of design options in a model
# doc   current document
def GetNumberOfDesignOptions(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rDoS.GetDesignOptions(doc).ToList())
    except:
        pass
    return number

# --------------------------------------------- VIEWS ---------------------------------------------

# returns the number of sheets in a model
# doc   current document
def GetNumberOfSheets(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rViews.GetSheetsInModel(doc))
    except:
        pass
    return number

# generic view filter allowing all views to be selected
def ViewFilter(view):
    return True

# returns the number of views in a model
# doc   current document
def GetViewsInTheModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rViews.GetViewsInModel(doc, ViewFilter))
    except:
        pass
    return number

# returns the number of views in a model
# doc   current document
def GetUnplacedViews(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rViews.GetViewsNotOnSheet(doc))
    except:
        pass
    return number

# --------------------------------------------- LINE STYLES / TYPES  ---------------------------------------------

# returns the number of line styles in a model
# doc   current document
def GetNumberOfLineStyles(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLsp.GetAllLineStyleIds(doc))
    except:
        pass
    return number

# returns the number of line styles in a model
# doc   current document
def GetNumberOfLinePatterns(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLsp.GetAllLinePatterns(doc))
    except:
        pass
    return number

# returns the number of fill patterns in a model
# doc   current document
def GetNumberOfFillPatterns(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLsp.GetAllFillPattern(doc))
    except Exception as e:
        print (e)
        pass
    return number

# --------------------------------------------- CAD links  ---------------------------------------------

# returns the number of CAD imports in a model
# doc   current document
def GetNumberOfCADImports(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLinks.GetCADTypeImportsOnly(doc))
    except:
        pass
    return number

# returns the number of CAD links to model in a model
# doc   current document
def GetNumberOfCADLinksToModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLinks.GetAllCADLinkTypeInModelOnly(doc))
    except:
        pass
    return number

# returns the number of CAD links to view
# doc   current document
def GetNumberOfCADLinksToView(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLinks.GetAllCADLinkTypeByViewOnly(doc))
    except:
        pass
    return number

# ---------------------------------------------  images  ---------------------------------------------

# returns the number of CAD links to view
# doc   current document
def GetNumberOfImageImports(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLinks.GetAllImageLinkTypeImportedInModel(doc))
    except:
        pass
    return number

# returns the number of CAD links to view
# doc   current document
def GetNumberOfImageLinks(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLinks.GetAllImageLinkTypeLinkedInModel(doc))
    except:
        pass
    return number

# ---------------------------------------------  Families  ---------------------------------------------

# returns the number of families in a model
# doc   current document
def GetNumberOfFamiliesInModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rFams.GetAllLoadableFamilies(doc))
    except:
        pass
    return number

# returns the number of in place families in a model
# doc   current document
def GetNumberOfInPlaceFamiliesInModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rFams.GetAllInPlaceFamilies(doc))
    except:
        pass
    return number

# ---------------------------------------------  Groups  ---------------------------------------------

# returns the number of detail groups in a model
# doc   current document
def GetNumberOfDetailGroupsInModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rGrp.GetDetailGroups(doc))
    except:
        pass
    return number

# returns the number of model groups in a model
# doc   current document
def GetNumberOfModelGroupsInModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rGrp.GetModelGroups(doc))
    except:
        pass
    return number

# returns the number of unplaced detail groups in a model
# doc   current document
def GetNumberOfUnplacedDetailGroupsInModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rGrp.GetUnplacedDetailGroups(doc))
    except:
        pass
    return number

# returns the number of unplaced model groups in a model
# doc   current document
def GetNumberOfUnplacedModelGroupsInModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rGrp.GetUnplacedModelGroups(doc))
    except:
        pass
    return number

# ---------------------------------------------  Rooms  ---------------------------------------------

# returns the number of unplaced rooms in a model
# doc   current document
def GetNumberOfRoomsInModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rRooms.GetAllRooms(doc))
    except:
        pass
    return number

# returns the number of unplaced rooms in a model
# doc   current document
def GetNumberOfUnplacedRoomsInModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rRooms.GetUnplacedRooms(doc))
    except:
        pass
    return number

# returns the number of redundant rooms in a model
# doc   current document
def GetNumberOfRedundantRoomsInModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rRooms.GetRedundantRooms(doc))
    except:
        pass
    return number

# returns the number of redundant rooms in a model
# doc   current document
def GetNumberOfNotEnclosedRoomsInModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rRooms.GetNotEnclosedRooms(doc))
    except:
        pass
    return number

# ---------------------------------------------  Detail Items  ---------------------------------------------

# returns the number of redundant rooms in a model
# doc   current document
def GetNumberOfFilledRegionInModel(doc):
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rDetItems.GetFilledRegionsInModel(doc))
    except:
        pass
    return number

# ----------------------------------------------
# main 
# ----------------------------------------------

#set up a named tuple to store data in it
healthDataAction = namedtuple('healthDataAction', 'getData reportFileName')

PARAM_ACTIONS = {
    'ValueWorksets': healthDataAction(GetWorksetNumber, rFns.PARAM_ACTIONS_FILENAME_NO_OF_WORKSETS),
    'ValueFileSize': healthDataAction(GetFileSize, rFns.PARAM_ACTIONS_FILENAME_FILE_SIZE),
    'ValueWarnings': healthDataAction(GetNumberOfWarnings, rFns.PARAM_ACTIONS_FILENAME_NO_OF_WARNINGS),
    'ValueDesignSets': healthDataAction(GetNumberOfDesignSets, rFns.PARAM_ACTIONS_FILENAME_NO_OF_DESIGN_SETS),
    'ValueDesignOptions': healthDataAction(GetNumberOfDesignOptions, rFns.PARAM_ACTIONS_FILENAME_NO_OF_DESIGN_OPTIONS),
    'ValueSheets': healthDataAction(GetNumberOfSheets, rFns.PARAM_ACTIONS_FILENAME_NO_OF_SHEETS),
    'ValueViews': healthDataAction(GetViewsInTheModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_VIEWS),
    'ValueViewsNotPlaced': healthDataAction(GetUnplacedViews, rFns.PARAM_ACTIONS_FILENAME_NO_OF_VIEWS_NOT_PLACED),
    'ValueLineStyles': healthDataAction(GetNumberOfLineStyles, rFns.PARAM_ACTIONS_FILENAME_NO_OF_LINE_STYLES),
    'ValueLinePatterns': healthDataAction(GetNumberOfLinePatterns, rFns.PARAM_ACTIONS_FILENAME_NO_OF_LINE_PATTERNS),
    'ValueFillPatterns': healthDataAction(GetNumberOfFillPatterns, rFns.PARAM_ACTIONS_FILENAME_NO_OF_FILL_PATTERNS),
    'ValueCADImports': healthDataAction(GetNumberOfCADImports, rFns.PARAM_ACTIONS_FILENAME_NO_OF_CAD_IMPORTS),
    'ValueCADLinksToModel': healthDataAction(GetNumberOfCADLinksToModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_CAD_LINKS_MODEL),
    'ValueCADLinksToView': healthDataAction(GetNumberOfCADLinksToView, rFns.PARAM_ACTIONS_FILENAME_NO_OF_CAD_LINKS_VIEW),
    'ValueImageImports': healthDataAction(GetNumberOfImageImports, rFns.PARAM_ACTIONS_FILENAME_NO_OF_IMAGE_IMPORTS),
    'ValueImageLinks': healthDataAction(GetNumberOfImageLinks, rFns.PARAM_ACTIONS_FILENAME_NO_OF_IMAGE_LINKS),
    'ValueFamilies': healthDataAction(GetNumberOfFamiliesInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_FAMILIES),
    'ValueFamiliesInPlace': healthDataAction(GetNumberOfInPlaceFamiliesInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_FAMILIES_IN_PLACE),
    'ValueModelGroups': healthDataAction(GetNumberOfModelGroupsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_MODEL_GROUPS),
    'ValueModelGroupsUnplaced': healthDataAction(GetNumberOfUnplacedModelGroupsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_MODEL_GROUPS_UNPLACED),
    'ValueDetailGroups': healthDataAction(GetNumberOfDetailGroupsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_DETAIL_GROUPS),
    'ValueDetailGroupsUnplaced': healthDataAction(GetNumberOfUnplacedDetailGroupsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_MODEL_GROUPS_UNPLACED),
    'ValueRooms': healthDataAction(GetNumberOfRoomsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_ROOMS),
    'ValueRoomsUnplaced': healthDataAction(GetNumberOfUnplacedRoomsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_UNPLACED),
    'ValueRoomsNotEnclosed': healthDataAction(GetNumberOfNotEnclosedRoomsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_UNENCLOSED),
    'ValueRoomsRedundant': healthDataAction(GetNumberOfRedundantRoomsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_REDUNDANT),
    'ValueFilledRegions': healthDataAction(GetNumberOfFilledRegionInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_FILLED_REGIONS)
}

# updates any instances of model health tracking family in a project
# doc   current document
def UpdateModelHealthTracerFamily(doc, revitFilePath):
    """updates model health tracker family"""
    revitFileName = util.GetFileNameWithoutExt(revitFilePath)
    resultValue = res.Result()
    instances = GetInstancesOfModelHealth(doc)
    if(len(instances) > 0):
        for instance in instances:
            updateFlag = GetParametersOfInstance(instance, doc)
            resultValue.Update(updateFlag)
    else:
        resultValue.UpdateSep(False, 'Family to update ' + MODEL_HEALTH_TRACKER_FAMILY + ' was not found in model: '+ revitFileName)
    return resultValue

# doc   current document
# revitFilePath     path of the curren document
def WriteModelHealthReport(doc, revitFilePath, ouputDirectory):
    """write out health tracker data"""
    revitFileName = util.GetFileNameWithoutExt(revitFilePath)
    resultValue = res.Result()
    # get values and write them out
    for key, value in PARAM_ACTIONS.items():
        pvalue = PARAM_ACTIONS[key].getData(doc)
        fileName = util.GetFileDateStamp() + revitFileName + PARAM_ACTIONS[key].reportFileName + '.temp'
        resExport = res.Result()
        try:
            util.writeReportData(
                ouputDirectory + '\\' + fileName,
                '',
                [[revitFileName, util.GetDateStamp(util.FILE_DATE_STAMP_YYYYMMDD_SPACE), util.GetDateStamp(util.TIME_STAMP_HHMMSEC_COLON), str(pvalue)]])
            resExport.UpdateSep(True, 'Exported: ' + str(key))
        except Exception as e:
                resExport.UpdateSep(True, 'Export failed: ' + str(key)+ ' ' + str(e))
        resultValue.Update(resExport)
    return resultValue
