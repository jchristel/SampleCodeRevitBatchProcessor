'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Model health report functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Model health report metrics can either be displayed in a family where each parameter is assigned to a metric 
and or data can be exported to text files which can be used to visualize key metrics over time.

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
clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)
import System

from duHast.Utilities import Utility as util
from duHast.APISamples import RevitBIM360 as b360
from duHast.APISamples import RevitCommonAPI as com
from duHast.Utilities import Result as res
from duHast.APISamples import RevitDesignSetOptions as rDoS
from duHast.APISamples import RevitWarnings as rWarn
from duHast.APISamples import RevitWorksets as rWork
from duHast.APISamples import RevitViews as rViews
from duHast.APISamples import RevitLineStylesPatterns as rLsp
from duHast.APISamples import RevitLinks as rLinks
from duHast.APISamples import RevitModelHealthReportFileNames as rFns
from duHast.APISamples import RevitFamilyUtils as rFams
from duHast.APISamples import RevitGroups as rGrp
from duHast.APISamples import RevitRooms as rRooms
from duHast.APISamples import RevitDetailItems as rDetItems
from duHast.APISamples import RevitElementParameterSetUtils as rParaSet

import Autodesk.Revit.DB as rdb
from System.Collections.Generic import List
from collections import namedtuple

# constants

#: A revit family displaying the health metrics retrieved by this code.
MODEL_HEALTH_TRACKER_FAMILY = 'Symbol_GraphicModelHealth_ANN'
#: Default value if unable to retrieve a health metric value from model
FAILED_TO_RETRIEVE_VALUE = -1

def _castParameterValue(pValue):
    '''
    Check if parameter is of type string ( currently the date only)
    and only cast to string if not...

    :param pValue: The parameter value
    :type pValue: unknown
    :return: The parameter value as a string
    :rtype: str
    '''
    
    newParaValue = ''
    if(pValue.GetType() != System.String):
        newParaValue = str(pValue)
    else:
        newParaValue = pValue
    return newParaValue

def GetInstancesOfModelHealth(doc):
    '''
    Gets all instances of the model health tracker family in a model.

    Built in parameter containing family name when filtering familyInstance elements:
    BuiltInParameter.ELEM_FAMILY_PARAM
    This is a faster filter in terms of performance then LINQ query refer to:
    https://jeremytammik.github.io/tbc/a/1382_filter_shortcuts.html

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list containing all model health tracker families in the model.
    :rtype: list of Autodesk.Revit.DB.FamilyInstance
    '''

    provider = rdb.ParameterValueProvider(rdb.ElementId(rdb.BuiltInParameter.ELEM_FAMILY_PARAM))
    evaluator = rdb.FilterStringEquals()
    rule = rdb.FilterStringRule( provider, evaluator, MODEL_HEALTH_TRACKER_FAMILY, True )
    filter = rdb.ElementParameterFilter( rule )
    return rdb.FilteredElementCollector(doc).OfClass(rdb.FamilyInstance).WherePasses(filter).ToList()

def GetParametersOfInstance(famInstance, doc):
    '''
    Updates parameter values of model tracker family instance.

    :param famInstance: An instance of the model health tracker family.
    :type famInstance: Autodesk.Revit.DB.FamilyInstance
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.
        
        - .result = True if all parameters where found on the family and got updated successfully or no update at all was required. Otherwise False.
        - .message will be 'Failed to get value for'
    
    :rtype: :class:`.Result`
    '''

    resultValue = res.Result()
    flagUpdate = False
    for p in famInstance.GetOrderedParameters():
        # check if parameter is read only
        if(p.IsReadOnly == False):
            # check an action to update this parameter value exists
            if(PARAM_ACTIONS.ContainsKey(p.Definition.Name)):
                parameterValue = PARAM_ACTIONS[p.Definition.Name].getData(doc)
                if(parameterValue != FAILED_TO_RETRIEVE_VALUE):
                    flag = rParaSet.set_parameter_value (p, _castParameterValue(parameterValue), doc)
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

def GetCurrentDate(doc):
    '''
    Get the current date

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: The current date in format YYYY_MM_DD.
    :rtype: str

    '''
    return util.GetFileDateStamp(util.FILE_DATE_STAMP_YYYY_MM_DD)

def GetWorksetNumber(doc):
    '''
    Gets the number of worksets in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: The number of worksets in a model.
    :rtype: int
    '''

    return len(rWork.GetWorksets(doc))

def GetFileSize(doc):
    '''
    Gets the file size in MB.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: File size in MB. On exception it will return -1
    :rtype: int
    '''

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

def GetNumberOfWarnings(doc):
    '''
    Gets the number of warnings in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of warnings in model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rWarn.GetWarnings(doc))
    except:
        pass
    return number

def GetNumberOfDesignSets(doc):
    '''
    Gets the number of design sets in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of design sets in model. On exception it will return -1
    :rtype: int
    '''
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rDoS.GetDesignSets(doc))
    except:
        pass
    return number

def GetNumberOfDesignOptions(doc):
    '''
    Gets the number of design options in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of design option in model. On exception it will return -1
    :rtype: int
    '''
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rDoS.GetDesignOptions(doc).ToList())
    except:
        pass
    return number

# --------------------------------------------- VIEWS ---------------------------------------------

def GetNumberOfSheets(doc):
    '''
    Gets the number of sheets in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of sheets in model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rViews.GetSheetsInModel(doc))
    except:
        pass
    return number

def _ViewFilter(view):
    '''
    generic view filter allowing all views to be selected

    :param view: not used!
    :type view: Autodesk.Revit.DB.View

    :return: returns always True
    :rtype: bool
    '''
    return True

def GetViewsInTheModel(doc):
    '''
    Gets the number of views in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of views in model. On exception it will return -1
    :rtype: int
    '''
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rViews.GetViewsInModel(doc, _ViewFilter))
    except:
        pass
    return number

def GetUnplacedViews(doc):
    '''
    Gets the number of unplaced views in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced views in model. On exception it will return -1
    :rtype: int
    '''
    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rViews.GetViewsNotOnSheet(doc))
    except:
        pass
    return number

# --------------------------------------------- LINE STYLES / TYPES  ---------------------------------------------

def GetNumberOfLineStyles(doc):
    '''
    Gets the number of line styles in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of line styles in model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLsp.GetAllLineStyleIds(doc))
    except:
        pass
    return number

def GetNumberOfLinePatterns(doc):
    '''
    Gets the number of line patterns in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of line patterns in model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLsp.GetAllLinePatterns(doc))
    except:
        pass
    return number

def GetNumberOfFillPatterns(doc):
    '''
    Gets the number of fill pattern in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of fill pattern in model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLsp.GetAllFillPattern(doc))
    except Exception as e:
        pass
    return number

# --------------------------------------------- CAD links  ---------------------------------------------

def GetNumberOfCADImports(doc):
    '''
    Gets the number of CAD imports in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of CAD imports in model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLinks.GetCADTypeImportsOnly(doc))
    except:
        pass
    return number

def GetNumberOfCADLinksToModel(doc):
    '''
    Gets the number of CAD links by model in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of CAD links by model in model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLinks.GetAllCADLinkTypeInModelOnly(doc))
    except:
        pass
    return number

def GetNumberOfCADLinksToView(doc):
    '''
    Gets the number of CAD links by view in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of CAD links by view in model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLinks.GetAllCADLinkTypeByViewOnly(doc))
    except:
        pass
    return number

# ---------------------------------------------  images  ---------------------------------------------

def GetNumberOfImageImports(doc):
    '''
    Gets the number of image imports in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of image imports in model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLinks.GetAllImageLinkTypeImportedInModel(doc))
    except:
        pass
    return number

def GetNumberOfImageLinks(doc):
    '''
    Gets the number of image links in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of image links in model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rLinks.GetAllImageLinkTypeLinkedInModel(doc))
    except:
        pass
    return number

# ---------------------------------------------  Families  ---------------------------------------------

def GetNumberOfFamiliesInModel(doc):
    '''
    Gets the number of families loaded into the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of families loaded into model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rFams.GetAllLoadableFamilies(doc))
    except:
        pass
    return number

def GetNumberOfInPlaceFamiliesInModel(doc):
    '''
    Gets the number of in-place families the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of in-place in the model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rFams.GetAllInPlaceFamilies(doc))
    except:
        pass
    return number

# ---------------------------------------------  Groups  ---------------------------------------------

def GetNumberOfDetailGroupsInModel(doc):
    '''
    Gets the number of detail group definitions the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of detail group definitions in the model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rGrp.GetDetailGroups(doc))
    except:
        pass
    return number

def GetNumberOfModelGroupsInModel(doc):
    '''
    Gets the number of model group definitions in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of model group definitions in the model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rGrp.GetModelGroups(doc))
    except:
        pass
    return number

def GetNumberOfUnplacedDetailGroupsInModel(doc):
    '''
    Gets the number of unplaced detail group definitions in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced detail group definitions in the model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rGrp.GetUnplacedDetailGroups(doc))
    except:
        pass
    return number

def GetNumberOfUnplacedModelGroupsInModel(doc):
    '''
    Gets the number of unplaced model group definitions in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced model group definitions in the model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rGrp.GetUnplacedModelGroups(doc))
    except:
        pass
    return number

# ---------------------------------------------  Rooms  ---------------------------------------------

def GetNumberOfRoomsInModel(doc):
    '''
    Gets the number of rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of rooms in the model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rRooms.GetAllRooms(doc))
    except:
        pass
    return number

def GetNumberOfUnplacedRoomsInModel(doc):
    '''
    Gets the number of unplaced rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of unplaced rooms in the model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rRooms.GetUnplacedRooms(doc))
    except:
        pass
    return number

def GetNumberOfRedundantRoomsInModel(doc):
    '''
    Gets the number of redundant rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of redundant rooms in the model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rRooms.GetRedundantRooms(doc))
    except:
        pass
    return number

def GetNumberOfNotEnclosedRoomsInModel(doc):
    '''
    Gets the not enclosed number of rooms in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of not enclosed rooms in the model. On exception it will return -1
    :rtype: int
    '''

    number = FAILED_TO_RETRIEVE_VALUE
    try:
        number = len(rRooms.GetNotEnclosedRooms(doc))
    except:
        pass
    return number

# ---------------------------------------------  Detail Items  ---------------------------------------------

def GetNumberOfFilledRegionInModel(doc):
    '''
    Gets the number of filled region instances in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Number of filled region instances in the model. On exception it will return -1
    :rtype: int
    '''
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

#: List of actions reporting model health metrics and their associated parameter name
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
    'ValueDetailGroupsUnplaced': healthDataAction(GetNumberOfUnplacedDetailGroupsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_DETAIL_GROUPS_UNPLACED),
    'ValueRooms': healthDataAction(GetNumberOfRoomsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_ROOMS),
    'ValueRoomsUnplaced': healthDataAction(GetNumberOfUnplacedRoomsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_UNPLACED),
    'ValueRoomsNotEnclosed': healthDataAction(GetNumberOfNotEnclosedRoomsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_UNENCLOSED),
    'ValueRoomsRedundant': healthDataAction(GetNumberOfRedundantRoomsInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_ROOMS_REDUNDANT),
    'ValueFilledRegions': healthDataAction(GetNumberOfFilledRegionInModel, rFns.PARAM_ACTIONS_FILENAME_NO_OF_FILLED_REGIONS),
    'ValueDateLastUpdated' : healthDataAction(GetCurrentDate, rFns.PARAM_ACTIONS_FILENAME_DATE_LAST_UPDATED)
}

def UpdateModelHealthTracerFamily(doc, revitFilePath):
    '''
    Updates instances of model health tracker family in project.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: Fully qualified revit model file path.
    :type revitFilePath: str

    :return: 
        Result class instance.
           
        - .result = True if all model key health metric where updated successfully. Otherwise False.
        - .message will be listing each parameter update: old value to new value
    
    :rtype: :class:`.Result`
    '''

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
# revitFilePath     path of the current document
def WriteModelHealthReport(doc, revitFilePath, outputDirectory):
    '''
    Write out health tracker data to file.

    Each value gets written to a separate file. The file name is made up of time stamp and the revit file name.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: Fully qualified revit model file path.
    :type revitFilePath: str
    :param outputDirectory: The directory path of where to write the data to.
    :type outputDirectory: str

    :return: 
        Result class instance.
        
        - .result = True if data was written to files successfully. Otherwise False.
        - .message will be contain data file path for each file.
    
    :rtype: :class:`.Result`
    '''
    
    revitFileName = util.GetFileNameWithoutExt(revitFilePath)
    resultValue = res.Result()
    # get values and write them out
    for key, value in PARAM_ACTIONS.items():
        parameterValue = PARAM_ACTIONS[key].getData(doc)
        fileName = util.GetFileDateStamp() + revitFileName + PARAM_ACTIONS[key].reportFileName + '.temp'
        resExport = res.Result()
        try:
            util.writeReportData(
                outputDirectory + '\\' + fileName,
                '',
                [
                    [
                        revitFileName, 
                        key, 
                        util.GetDateStamp(util.FILE_DATE_STAMP_YYYYMMDD_SPACE), 
                        util.GetDateStamp(util.TIME_STAMP_HHMMSEC_COLON), 
                        _castParameterValue(parameterValue)
                        ]
                    ]
                )
                
            resExport.UpdateSep(True, 'Exported: ' + str(key))
        except Exception as e:
                resExport.UpdateSep(True, 'Export failed: ' + str(key)+ ' ' + str(e))
        resultValue.Update(resExport)
    return resultValue
