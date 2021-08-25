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
import RevitFamilyUtils as rFams
import RevitGroups as rGrp
import RevitRooms as rRooms
import RevitDetailItems as rDetItems

from Autodesk.Revit.DB import *
from System.Collections.Generic import List

# constants
# health tracer family name
MODEL_HEALTH_TRACKER_FAMILY = 'Symbol_GraphicModelHealth_ANN'
# default value if unable to retrieve value from model
FAILED_TO_RETRIEVE_VALUE = -1

# gets all instances of the model health tracker family in a model
# doc   current document
def GetInstancesOfModelHealth(doc):
    # built in parameter containing family name when filtering familyInstance elements:
    # BuiltInParameter.ELEM_FAMILY_PARAM
    # this is a faster filter in terms of performance then LINQ query refer to:
    # https://jeremytammik.github.io/tbc/a/1382_filter_shortcuts.html
    provider = ParameterValueProvider(ElementId(BuiltInParameter.ELEM_FAMILY_PARAM))
    evaluator = FilterStringEquals()
    rule = FilterStringRule( provider, evaluator, MODEL_HEALTH_TRACKER_FAMILY, True )
    filter = ElementParameterFilter( rule )
    return FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(filter).ToList()

# update parameter values of model tracker family instance
# famInstance   an instance of the family model health tracker
# doc           current document
def GetParametersOfInstance(famInstance, doc):
    resultValue = res.Result()
    flagUpdate = False
    for p in famInstance.GetOrderedParameters():
        # check if parameter is read only
        if(p.IsReadOnly == False):
            for parameterAction in PARAM_ACTIONS:
                if(p.Definition.Name == parameterAction[0]):
                    pvalue = parameterAction[1](doc)
                    if(pvalue != FAILED_TO_RETRIEVE_VALUE):
                        flag = com.setParameterValue(p, str(pvalue), doc)
                        resultValue.Update(flag)
                        # print (str(p.Definition.Name) + ' :: ' +str(flag.message))
                        flagUpdate = True
                        break
                    else:
                        resultValue.UpdateSep(False, 'Failed to get value for ' + p.Definition.Name)
                        break
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

# list containing parameter names and the action getting the integer value for the parameter
PARAM_ACTIONS = [
    ['ValueWorksets', GetWorksetNumber],
    ['ValueFileSize', GetFileSize],
    ['ValueWarnings', GetNumberOfWarnings],
    ['ValueDesignSets', GetNumberOfDesignSets],
    ['ValueDesignOptions', GetNumberOfDesignOptions],
    ['ValueSheets', GetNumberOfSheets],
    ['ValueViews', GetViewsInTheModel],
    ['ValueViewsNotPlaced', GetUnplacedViews],
    ['ValueLineStyles', GetNumberOfLineStyles],
    ['ValueLinePatterns', GetNumberOfLinePatterns],
    ['ValueFillPatterns', GetNumberOfFillPatterns],
    ['ValueCADImports', GetNumberOfCADImports],
    ['ValueCADLinksToModel', GetNumberOfCADLinksToModel],
    ['ValueCADLinksToView', GetNumberOfCADLinksToView],
    ['ValueImageImports', GetNumberOfImageImports],
    ['ValueImageLinks', GetNumberOfImageLinks],
    ['ValueFamilies', GetNumberOfFamiliesInModel],
    ['ValueFamiliesInPlace', GetNumberOfInPlaceFamiliesInModel],
    ['ValueModelGroups', GetNumberOfModelGroupsInModel],
    ['ValueModelGroupsUnplaced', GetNumberOfUnplacedModelGroupsInModel],
    ['ValueDetailGroups', GetNumberOfDetailGroupsInModel],
    ['ValueDetailGroupsUnplaced', GetNumberOfUnplacedDetailGroupsInModel],
    ['ValueRooms', GetNumberOfRoomsInModel],
    ['ValueRoomsUnplaced', GetNumberOfUnplacedRoomsInModel],
    ['ValueRoomsNotEnclosed', GetNumberOfNotEnclosedRoomsInModel],
    ['ValueRoomsRedundant', GetNumberOfRedundantRoomsInModel],
    ['ValueFilledRegions', GetNumberOfFilledRegionInModel]
]

# updates any instances of model health tracking family in a project
# doc   current document
def UpdateModelHealthTracerFamily(doc, revitFilePath):
    # the current file name
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