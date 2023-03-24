'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit links, CAD links and image links.
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
from duHast.APISamples import RevitElementParameterGetUtils as rParaGet
from duHast.Utilities import Result as res
from duHast.APISamples import RevitTransaction as rTran
from duHast.Utilities import Utility as util
import glob
import os
from os import path

# import Autodesk
import Autodesk.Revit.DB as rdb



# -------------------------------------------- common variables --------------------

#: revit links header used in reports
REPORT_REVIT_LINKS_HEADER = [
    'HOSTFILE',
    'ID', 
    'LINKNAME',
    'ISLOADED',
    'TYPEWORKSET',
    'ISFROMLOCALPATH',
    'PATHTYPE',
    'FILEPATH',
    'SHAREDSITE', 
    'SHAREDSITENAME', 
    'INSTANCEWORKSET', 
    'DESIGNOPTION',
]

#: CAD links header used in reports
REPORT_CAD_LINKS_HEADER = [
    'HOSTFILE',
    'ID', 
    'LINKNAME', 
    'ISVIEWSPECIFIC', 
    'VIEWID', 
    'WORKSET', 
    'DESIGNOPTION',
    'ISPINNED',
    'DRAWLAYER', 
    'FILEPATH'
]

# -------------------------------------------- CAD Links -------------------------------------------------

def GetAllCADLinkTypes(doc):
    '''
    Gets all CAD link types in a model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of CAD link types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.CADLinkType)
    return collector

def GetAllCADLinkInstances(doc):
    '''
    Gets all CAD link instances in a model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of import instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ImportInstance)
    return collector

def GetCADTypeImportsOnly(doc):
    '''
    Gets all CAD imports in a model.

    Filters by class and check whether the element is an external file reference (True its a link, False it is an import)
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of all CAD imports in a model.
    :rtype: list Autodesk.Revit.DB.CADLinkType
    '''

    cadImports = []
    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.CADLinkType)
    for cad in collector:
        if(cad.IsExternalFileReference() == False):
            cadImports.append(cad)
    return cadImports

def SortCADLinkTypesByModelOrViewSpecific(doc):
    '''
    Returns two lists: First one: cad links types linked by view (2D) , second one cad link types linked into model (3D).

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Two lists of cad link types.
    :rtype: list Autodesk.Revit.DB.CADLinkType, list Autodesk.Revit.DB.CADLinkType
    '''

    cadLinksByView = []
    cadLinksByModel = []
    collectorCADTypes = GetAllCADLinkTypes(doc)
    collectorCADInstances = GetAllCADLinkInstances(doc)
    idsByView = []
    # work out through the instance which cad link type is by view
    for cInstance in collectorCADInstances:
        if(cInstance.ViewSpecific):
            idsByView.append(cInstance.GetTypeId())
    # filter all cad link types by id's identified
    for cType in collectorCADTypes:
        if(cType.Id in idsByView and cType.IsExternalFileReference()):
            cadLinksByView.append(cType)
        elif(cType.IsExternalFileReference()):
            cadLinksByModel.append(cType)
    return cadLinksByView, cadLinksByModel

def GetAllCADLinkTypeByViewOnly(doc):
    '''
    Gets all CAD links by view in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Lists of cad link types.
    :rtype: list Autodesk.Revit.DB.CADLinkType
    '''

    cadLinksByView, cadLinksByModel = SortCADLinkTypesByModelOrViewSpecific(doc)
    return cadLinksByView

def GetAllCADLinkTypeInModelOnly(doc):
    '''
    Gets all CAD links by model in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Lists of cad link types.
    :rtype: list Autodesk.Revit.DB.CADLinkType
    '''

    cadLinksByView, cadLinksByModel = SortCADLinkTypesByModelOrViewSpecific(doc)
    return cadLinksByModel

def DeleteCADLinks(doc):
    '''
    Deletes all CAD links in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: 
        Result class instance.
            
        - .result = True if all CAD links got deleted. Otherwise False.
        - .message will contain status of deletion.

    :rtype: :class:`.Result`
    '''

    ids = []
    returnValue = res.Result()
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.ImportInstance):
        ids.append(p.Id)
    # delete all links at once
    returnValue = com.DeleteByElementIds(doc, ids, 'Deleting CAD links', 'CAD link(s)')
    return returnValue

def ReloadCADLinks(doc, linkLocations, hostNameFormatted, doSomethingWithLinkName):
    '''
    Reloads CAD links from a given file location based on the original link type name (starts with comparison)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param linkLocations: A list of directories where CAD files can be located.
    :type linkLocations: list str
    :param hostNameFormatted: Not used yet
    :type hostNameFormatted: TBC
    :param doSomethingWithLinkName: A function which amends the link name prior search for a match in folders.\
        I.e. can be used to truncate the link name i.e. the revision details of a link
    :type doSomethingWithLinkName: func(str) -> str

    :return: 
        Result class instance.

        - .result = True if all CAD links got reloaded successfully. Otherwise False.
        - .message will contain status of reload and fully qualified file name. On exception it will also include the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        # get all CAD link types in model
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.CADLinkType):
            linkTypeName = doSomethingWithLinkName(rdb.Element.Name.GetValue(p))
            newLinkPath = 'unknown'
            try:
                newLinkPath = GetLinkPath(linkTypeName, linkLocations, '.dwg')
                if(newLinkPath != None):
                    # reloading CAD links requires a transaction
                    def action():
                        actionReturnValue = res.Result()
                        try:
                            result = p.LoadFrom(newLinkPath)
                            actionReturnValue.message = linkTypeName + ' :: ' + str(result.LoadResult)
                        except Exception as e:
                            actionReturnValue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
                        return actionReturnValue
                    transaction = rdb.Transaction(doc, 'Reloading: ' + linkTypeName)
                    reloadResult = rTran.in_transaction(transaction, action)
                    returnValue.Update(reloadResult)
                else:
                    returnValue.UpdateSep(False, linkTypeName + ' :: ' + 'No link path or multiple path found in provided locations')
            except Exception as e:
                returnValue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnValue

# ------------------------------------------------------- CAD link geometry --------------------------------------------------------------------

def GetCADImportInstanceGeometry(importInstance):
    '''
    Returns a list of geometry elements from an import instance

    :param importInstance: A import instance
    :type importInstance: AutoDesk.Revit.DB.ImportInstance
    
    :return: A list of geometry objects. Can return an empty list!
    :rtype: [Autodesk.Revit.DB GeometryObject]
    '''

    geo = []
    # default geometry option
    opt = rdb.Options()
    geoElemLevel1 = importInstance.get_Geometry(opt)
    if (geoElemLevel1 != None):
        for geoInstance in geoElemLevel1:
            if(geoInstance!= None):
                geoElemLevel2 = geoInstance.GetInstanceGeometry()
                if(geoElemLevel2 !=None):
                    for item in geoElemLevel2:
                        geo.append(item)
    return geo

def GetAllCADImportInstancesGeometry(doc):
    '''
    Returns a list of geometry elements from all import instances in the document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of geometry objects. Can return an empty list!
    :rtype: [Autodesk.Revit.DB GeometryObject]
    '''
    instancesGeometry = []
    allImportInstances = GetAllCADLinkInstances(doc)
    for importInstance in allImportInstances:
        geometryInstances = GetCADImportInstanceGeometry(importInstance)
        if (len(geometryInstances) > 0):
            instancesGeometry += geometryInstances
    return instancesGeometry


# ------------------------------------------------------- CAD link reporting --------------------------------------------------------------------

def GetCADLinkTypeDataByName(cadLinkName, doc, revitFilePath):
    '''
    Extract the file path from CAD link type.

    :param cadLinkName: The cad link name
    :type cadLinkName: str
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The fully qualified file path to the model.
    :type revitFilePath: str

    :return: The fully qualified file path if the cad link type is a valid external reference.\
        Otherwise it will return 'unknown'.
    :rtype: str
    '''

    #default values
    modelPath = 'unknown'
    for p in rdb.FilteredElementCollector(doc).OfClass(rdb.CADLinkType):
        if (rdb.Element.Name.GetValue(p) == cadLinkName):
            try:
                exFileRef = p.GetExternalFileReference()
                if(exFileRef.IsValidExternalFileReference(exFileRef)):
                    modelPath = rdb.ModelPathUtils.ConvertModelPathToUserVisiblePath(exFileRef.GetPath())
                    modelPath = util.ConvertRelativePathToFullPath(modelPath, revitFilePath)
                break
            except Exception as e:
                modelPath = str(e)
    return modelPath

def GetCADReportData(doc, revitFilePath):
    '''
    Gets CAD link data to be written to report file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The fully qualified file path to the model, which is added to data returned.
    :type revitFilePath: str

    :return: list of list of cad link properties.
    :rtype: list of list of str
    '''

    data = []
    collector = GetAllCADLinkInstances(doc)
    for c in collector:
        # get the workset
        wsParam = c.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
        # get the design option
        doParam = c.get_Parameter(rdb.BuiltInParameter.DESIGN_OPTION_ID)
        # get the link name, link type name and shared coordinates (true or false)
        lNameParam = c.get_Parameter(rdb.BuiltInParameter.IMPORT_SYMBOL_NAME)
        # get the draw layer
        lDrawLayerParam = c.get_Parameter(rdb.BuiltInParameter.IMPORT_BACKGROUND)
        # get shared location?
        # lSharedParam = cadLink.get_Parameter(BuiltInParameter.GEO_LOCATION)
        isViewSpecific= c.ViewSpecific
        ownerViewId = c.OwnerViewId
        linkTypeData = GetCADLinkTypeDataByName(lNameParam.AsString(), doc, revitFilePath)
        data.append([
            revitFilePath, 
            str(c.Id), 
            str(lNameParam.AsString()), 
            str(isViewSpecific), 
            str(ownerViewId), 
            str(wsParam.AsValueString()), 
            str(doParam.AsString()),
            str(c.Pinned), 
            str(lDrawLayerParam.AsValueString()),
            linkTypeData])
    return data

# -------------------------------------------- Revit Links -------------------------------------------------

def GetAllRevitLinkInstances(doc):
    '''
    Gets all Revit link instances in a model.

    Filters by class.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of revit link instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkInstance)
    return collector

def GetAllRevitLinkTypes(doc):
    '''
    Gets all Revit link types in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of revit link types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkType)
    return collector
    
def GetRevitLinkTypeFromInstance(doc, linkInstance):
    '''
    Gets the Revit link type from a given revit link instance.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param linkInstance: The link instance the type of is to be returned
    :type linkInstance: Autodesk.Revit.DB.RevitLinkInstance

    :return: The matching revit link type.
    :rtype: Autodesk.Revit.DB.RevitLinkType
    '''
    
    revitLinkTypes = GetAllRevitLinkTypes(doc)
    for lt in revitLinkTypes:
        if(lt.Id == linkInstance.GetTypeId()):
            return lt

def DeleteRevitLinks(doc):
    '''
    Deletes all revit links in a file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: 
        Result class instance.
        
        - .result = True if all revit links got deleted successfully. Otherwise False.
        - .message will contain deletion status. On exception it will also include the exception message.
    
    :rtype: :class:`.Result`
    '''

    ids = []
    returnValue = res.Result()
    for p in rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_RvtLinks):
        ids.append(p.Id)
    # delete all links at once
    returnValue = com.DeleteByElementIds(doc, ids, 'Deleting Revit links', 'Revit link(s)')
    return returnValue

def ReloadRevitLinks(doc, linkLocations, hostNameFormatted, doSomethingWithLinkName, worksetConfig):
    '''
    Reloads Revit links from a given file location based on the original link type name (starts with comparison)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param linkLocations: A list of directories where CAD files can be located.
    :type linkLocations: list str
    :param hostNameFormatted: Not used yet
    :type hostNameFormatted: TBC
    :param doSomethingWithLinkName: A function which amends the link name prior search for a match in folders.\
        I.e. can be used to truncate the link name i.e. the revision details of a link
    :type doSomethingWithLinkName: func(str) -> str
    :param worksetConfig: To use the previously applied workset config use None, otherwise provide custom config.
    :type worksetConfig: Autodesk.Revit.DB.WorksetConfiguration

    :return: 
        Result class instance.
        
        - .result = True if all revit links got reloaded successfully. Otherwise False.
        - .message will contain status of reload and fully qualified file name. On exception it will also include the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        # get all revit link types in model
        for p in rdb.FilteredElementCollector(doc).OfClass(rdb.RevitLinkType):
            linkTypeName = doSomethingWithLinkName(rdb.Element.Name.GetValue(p))
            newLinkPath = 'unknown'
            try:
                newLinkPath = GetLinkPath(linkTypeName, linkLocations, '.rvt')
                if(newLinkPath != None):
                    mp = rdb.ModelPathUtils.ConvertUserVisiblePathToModelPath(newLinkPath)
                    # attempt to reload with worksets set to last viewed
                    # wc = WorksetConfiguration(WorksetConfigurationOption.OpenLastViewed)
                    # however that can be achieved also ... According to Autodesk:
                    # If you want to load the same set of worksets the link previously had, leave this argument as a null reference ( Nothing in Visual Basic) .
                    wc = worksetConfig()
                    result = p.LoadFrom(mp,  wc)
                    # store result in message 
                    returnValue.AppendMessage(linkTypeName + ' :: ' + str(result.LoadResult))
                else:
                    returnValue.UpdateSep(False, linkTypeName + ' :: ' + 'No link path or multiple path found in provided locations')
            except Exception as e:
                returnValue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnValue

def ReloadRevitLinksFromList(doc, linkTypesTobReloaded, linkLocations, hostNameFormatted, doSomethingWithLinkName, worksetConfig):
    '''
    Reloads Revit links from a given file location based on the original link type name (starts with comparison)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param linkTypesTobReloaded: List of link type elements to be reloaded.
    :type linkTypesTobReloaded: list Autodesk.Revit.DB.RevitLinkType
    :param linkLocations: A list of directories where CAD files can be located.
    :type linkLocations: list str
    :param hostNameFormatted: Not used yet
    :type hostNameFormatted: TBC
    :param doSomethingWithLinkName: A function which amends the link name prior search for a match in folders.\
        I.e. can be used to truncate the link name i.e. the revision details of a link
    :type doSomethingWithLinkName: func(str) -> str
    :param worksetConfig: To use the previously applied workset config use None, otherwise provide custom config.
    :type worksetConfig: Autodesk.Revit.DB.WorksetConfiguration

    :return: 
        Result class instance.
        
        - .result = True if all revit links got reloaded successfully. Otherwise False.
        - .message will contain status of reload and fully qualified file name. On exception it will also include the exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    try:
        # loop over links supplied
        for p in linkTypesTobReloaded:
            linkTypeName = doSomethingWithLinkName(rdb.Element.Name.GetValue(p))
            newLinkPath = 'unknown'
            try:
                newLinkPath = GetLinkPath(linkTypeName, linkLocations, '.rvt')
                if(newLinkPath != None):
                    mp = rdb.ModelPathUtils.ConvertUserVisiblePathToModelPath(newLinkPath)
                    # attempt to reload with worksets set to last viewed
                    # wc = WorksetConfiguration(WorksetConfigurationOption.OpenLastViewed)
                    # however that can be achieved also ... According to Autodesk:
                    # If you want to load the same set of worksets the link previously had, leave this argument as a null reference ( Nothing in Visual Basic) .
                    wc = worksetConfig()
                    result = p.LoadFrom(mp,  wc)
                    # store result in message 
                    returnValue.AppendMessage(linkTypeName + ' :: ' + str(result.LoadResult))
                else:
                    returnValue.UpdateSep(False, linkTypeName + ' :: ' + 'No link path or multiple path found in provided locations')
            except Exception as e:
                returnValue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
    except Exception as e:
        returnValue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnValue

def GetLinkPath(fileName, possibleLinkLocations, fileExtension):
    '''
    Gets a fully qualified file path to a file name match (revit project file extension .rvt) in given directory locations.

    Returns the first file name match it finds! If no match found returns None.

    :param fileName: Filter to identify match. Filter is string.startswith(fileName)
    :type fileName: str
    :param possibleLinkLocations: List of folders which may contain the link file.
    :type possibleLinkLocations: list str
    :param fileExtension: A file extension in format: '.xyz'. Use '.rvt' for revit project files.
    :type fileExtension: str
    :return: Fully qualified file path if match is found otherwise None.
    :rtype: str
    '''

    linkPath = None
    counter = 0
    try:
        foundMatch = False
        # attempt to find filename match in given locations
        for linkLocation in possibleLinkLocations:
            fileList = glob.glob(linkLocation + '\\*' + fileExtension)
            if (fileList != None):
                for file in fileList:
                    fileNameInFolder = path.basename(file)
                    if (fileNameInFolder.startswith(fileName)):
                        linkPath = file
                        counter =+ 1
                        foundMatch = True
                        break
        # return none if multiple matches where found            
        if(foundMatch == True and counter > 1):
            linkPath = None
    except Exception:
        linkPath = None
    return linkPath

def DefaultLinkName(name):
    '''
    Default 'do something with link name' method. Returns the link name unchanged.

    Could be replaced with something which i.e. truncates the revision...

    :param name: The link name.
    :type name: str

    :return: the link name unchanged.
    :rtype: str
    '''

    return name

def DefaultWorksetConfigForReload():
    '''
    Default method returning a open previous workset configuration. (None)

    :return: None: which is use the previous workset configuration.
    :rtype: None
    '''

    return None

# ------------------------------------------------------- Revit link reporting --------------------------------------------------------------------

def GetRevitLinkTypeData(doc, revitLinkType):
    '''
    Gets Revit Link Type data for reporting.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitLinkType: The link type of which to get the data from.
    :type revitLinkType: Autodesk.Revit.DB.RevitLinkType

    :return: A list of string 
    :rtype: list str
    '''

    # default values
    modelPath = 'unknown'
    isLoaded = False
    isFromLocalPath = False
    pathType = 'unknown'
    isLoaded = revitLinkType.IsLoaded(doc, revitLinkType.Id)
    isFromLocalPath = revitLinkType.IsFromLocalPath()
    exFileRef = revitLinkType.GetExternalFileReference()
    # get the workset of the link type (this can bew different to the workset of the link instance)
    wsParameter = revitLinkType.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
    if(exFileRef.IsValidExternalFileReference(exFileRef)):
        modelPath = rdb.ModelPathUtils.ConvertModelPathToUserVisiblePath(exFileRef.GetPath())
        pathType = exFileRef.PathType.ToString()

    data=[
        rdb.Element.Name.GetValue(revitLinkType),
        str(isLoaded), 
        str(wsParameter.AsValueString()), 
        str(isFromLocalPath), 
        pathType, 
        modelPath]
      
    return data

def GetRevitLinkReportData(doc, revitFilePath):
    '''
    Gets link data ready for being printed to file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revitFilePath: The file hostname, which is added to data returned.
    :type revitFilePath: str

    :return: list of list of revit link properties.
    :rtype: list of list of str
    '''

    data = []
    collector = GetAllRevitLinkInstances(doc)
    for c in collector:
        # get the workset
        wsParameter = c.get_Parameter(rdb.BuiltInParameter.ELEM_PARTITION_PARAM)
        # get the design option
        doParameter = c.get_Parameter(rdb.BuiltInParameter.DESIGN_OPTION_ID)
        # get whether link is shared or not (only works when link is loaded)
        if ('<Not Shared>' in c.Name):
            lS = False 
        else: 
            lS = True 
        # get shared location name ( needs to be in try catch in case file is unloaded)
        linkLocationName = 'unknown'
        try:
            linkLocationName = c.GetLinkDocument().ActiveProjectLocation.Name
        except Exception:
            pass
        linkType = GetRevitLinkTypeFromInstance(doc, c)
        linkTypeData = GetRevitLinkTypeData(doc, linkType)
        # add other data
        linkTypeData = [revitFilePath] + [str(c.Id)] + linkTypeData + [str(lS)] +[linkLocationName] + [rParaGet.get_parameter_value (wsParameter)] + [rParaGet.get_parameter_value(doParameter)]
        data.append(linkTypeData)
    return data
        
# -------------------------------------------- IMAGES -------------------------------------------------

def GetImagesTypesInModel(doc):
    '''
    Gets all image link types and image link instances in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of image types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.ImageType)
    return collector

def GetImagesTypeIdsInModel(doc):
    '''
    Gets all image link type Ids and image link instance ids in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing image types and image instances.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = GetImagesTypesInModel(doc)
    ids = com.GetIdsFromElementCollector(col)
    return ids


def SortImageLinkTypesByImportOrLinked(doc):
    '''
    Returns two lists: First one: images linked into model, second one images saved into model from model itself (no external file reference)

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Two lists of image types and instances (?)
    :rtype: list Autodesk.Revit.DB.ImageType, list Autodesk.Revit.DB.ImageType 
    '''

    imageLink = []
    imageImport = []
    collectorImageTypes = GetImagesTypesInModel(doc)
    for im in collectorImageTypes:
        if(im.IsLoadedFromFile()):
            imageLink.append(im)
        else:
            imageImport.append(im)
    return imageLink, imageImport

def GetAllImageLinkTypeLinkedInModel(doc):
    '''
    Gets all image link types which are links (external referenced) in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of image types and instances (?)
    :rtype: list Autodesk.Revit.DB.ImageType
    '''

    imageLinks, imageImport = SortImageLinkTypesByImportOrLinked(doc)
    return imageLinks

def GetAllImageLinkTypeImportedInModel(doc):
    '''
    Gets all image link types which are imported (not an external reference) in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of image types and instances (?)
    :rtype: list Autodesk.Revit.DB.ImageType
    '''

    imageLinks, imageImport = SortImageLinkTypesByImportOrLinked(doc)
    return imageImport

def GetImageTypeInModel(doc):
    '''
    Gets all image types in a model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of image types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_RasterImages).WhereElementIsElementType()

def GetImageInstancesInModel(doc):
    '''
    Gets all image instances placed in a model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of image instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    return rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_RasterImages).WhereElementIsNotElementType()

def GetAllUnusedImageTypeIdsInModel(doc):
    '''
    Gets all image types with no instances placed in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of ids representing image types.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    unusedImages = com.GetNotPlacedTypes(doc, GetImageTypeInModel, GetImageInstancesInModel)
    unusedTypeIds = []
    for i in unusedImages:
        unusedTypeIds.append(i.Id)
    return unusedTypeIds

def GetAllUnusedImageTypeIdsInModelWithGroupCheck(doc):
    '''
    Gets all image types with no instance placed in a model but includes group definition check.

    This only returns valid data if at least one instance of the group is placed in the model!!
    Otherwise images in groups which are not placed will not be flagged by this filter!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing image types.
    :rtype: list  Autodesk.Revit.DB.ElementId
    '''

    unusedTypeIds = GetAllUnusedImageTypeIdsInModel(doc)
    # and filter by any type id's in groups which may not be placed and hence no instance present in the model
    unusedTypeIds = com.GetUnusedTypeIdsFromDetailGroups(doc, unusedTypeIds)
    return unusedTypeIds