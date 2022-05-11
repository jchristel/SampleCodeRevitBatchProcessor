'''
This module contains a number of helper functions relating to Revit links, CAD links and image links. 
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
import RevitCommonAPI as com
import Result as res
import Utility as util
import glob
import os
from os import path

# import Autodesk
from Autodesk.Revit.DB import FilteredElementCollector, CADLinkType, ImportInstance, Element, BuiltInParameter, Transaction, ModelPathUtils,\
    RevitLinkInstance, RevitLinkType, BuiltInCategory, ImageType

clr.ImportExtensions(System.Linq)

# -------------------------------------------- common variables --------------------

# revit links header used in reports
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

# CAD links header used in reports
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

# doc   current model document
def GetAllCADLinkTypes(doc):
    '''returns all CAD link types in a model'''
    collector = FilteredElementCollector(doc).OfClass(CADLinkType)
    return collector

# doc   current model document
def GetAllCADLinkInstances(doc):
    '''returns all CAD link instances in a model'''
    collector = FilteredElementCollector(doc).OfClass(ImportInstance)
    return collector

# doc   current model document
def GetCADTypeImportsOnly(doc):
    '''returns all CAD imports in a model'''
    cadImports = []
    collector = FilteredElementCollector(doc).OfClass(CADLinkType)
    for cad in collector:
        if(cad.IsExternalFileReference() == False):
            cadImports.append(cad)
    return cadImports

# doc   current model document
def SortCADLinkTypesByModelOrViewSpecific(doc):
    '''returns two lists: First one: cad links types linked by view, second one cad link types linked into model'''
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

# doc   current odel document
def GetAllCADLinkTypeByViewOnly(doc):
    '''returns all CAD links by view in a model'''
    cadLinksByView, cadLinksByModel = SortCADLinkTypesByModelOrViewSpecific(doc)
    return cadLinksByView

# doc   current model document
def GetAllCADLinkTypeInModelOnly(doc):
    '''returns all CAD links by view in a model'''
    cadLinksByView, cadLinksByModel = SortCADLinkTypesByModelOrViewSpecific(doc)
    return cadLinksByModel

# doc:              the current model document
def DeleteCADLinks(doc):
    '''deletes all CAD links in a file'''
    ids = []
    returnvalue = res.Result()
    for p in FilteredElementCollector(doc).OfClass(ImportInstance):
        ids.append(p.Id)
    # delete all links at once
    returnvalue = com.DeleteByElementIds(doc, ids, 'Deleting CAD links', 'CAD link(s)')
    return returnvalue

# link locations: a list of directories where the revit files can be located
# dosomethingwithLinkName can be used to truncate i.e. the revision details of a link
def ReloadCADLinks(doc, linkLocations, hostNameFormatted, doSomethingWithLinkName):
    '''reloads CAD links from a given location based on the original link type name (starts with)'''
    returnvalue = res.Result()
    try:
        # get all CAD link types in model
        for p in FilteredElementCollector(doc).OfClass(CADLinkType):
            linkTypeName = doSomethingWithLinkName(Element.Name.GetValue(p))
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
                    transaction = Transaction(doc, 'Reloading: ' + linkTypeName)
                    reloadResult = com.InTransaction(transaction, action)
                    returnvalue.Update(reloadResult)
                else:
                    returnvalue.UpdateSep(False, linkTypeName + ' :: ' + 'No link path or multiple path found in provided locations')
            except Exception as e:
                returnvalue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnvalue

# ------------------------------------------------------- CAD link reporting --------------------------------------------------------------------

# cadLinkName:      the cad link name
# doc:              the current model document
# returns 'unknown' if path is not a valid external file reference
def GetCADLinkTypeDataByName(cadLinkName, doc, revitFilePath):
    '''extract the path from CAD link type'''
    #default values
    modelPath = 'unknown'
    for p in FilteredElementCollector(doc).OfClass(CADLinkType):
        if (Element.Name.GetValue(p) == cadLinkName):
            try:
                exFileRef = p.GetExternalFileReference()
                if(exFileRef.IsValidExternalFileReference(exFileRef)):
                    modelPath = ModelPathUtils.ConvertModelPathToUserVisiblePath(exFileRef.GetPath())
                    modelPath = util.ConvertRelativePathToFullPath(modelPath, revitFilePath)
                break
            except Exception as e:
                modelPath = str(e)
    return modelPath

# doc: the current revit document
# revitFilePath: fully qualified file path of Revit file
# returns a list of lists
def GetCADReportData(doc, revitFilePath):
    '''gets CAD links data ready for being printed to file'''
    data = []
    collector = GetAllCADLinkInstances(doc)
    for c in collector:
        # get the workset
        wsParam = c.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        # get the design option
        doParam = c.get_Parameter(BuiltInParameter.DESIGN_OPTION_ID)
        # get the link name, link type name and shared coordinates (true or false)
        lNameParam = c.get_Parameter(BuiltInParameter.IMPORT_SYMBOL_NAME)
        # get the draw layer
        lDrawLayerParam = c.get_Parameter(BuiltInParameter.IMPORT_BACKGROUND)
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

# doc   current model document
'''returns all Revit link instances in a model'''
def GetAllRevitLinkInstances(doc):
    collector = FilteredElementCollector(doc).OfClass(RevitLinkInstance)
    return collector

# doc   current model document
def GetAllRevitLinkTypes(doc):
    '''returns all Revit link types in a model'''
    collector = FilteredElementCollector(doc).OfClass(RevitLinkType)
    return collector

# doc               current model document
# linkInstance:     the linkinstance the type of is to be returned
def GetRevitLinkTypeFromInstance(doc, linkInstance):
    '''returns all Revit link type from a given instance'''
    revitLinkTypes = GetAllRevitLinkTypes(doc)
    for lt in revitLinkTypes:
        if(lt.Id == linkInstance.GetTypeId()):
            return lt

# doc:      current model document
def DeleteRevitLinks(doc):
    '''deletes all revit links in a file'''
    ids = []
    returnvalue = res.Result()
    for p in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RvtLinks):
        ids.append(p.Id)
    # delete all links at once
    returnvalue = com.DeleteByElementIds(doc, ids, 'Deleting Revit links', 'Revit link(s)')
    return returnvalue

# link locations: a list of directories where the revit files can be located
# dosomethingwithLinkName can be used to truncate i.e. the revision details of a link
# worksetconfig: None: to use the previously apllied workset config
def ReloadRevitLinks(doc, linkLocations, hostNameFormatted, doSomethingWithLinkName, worksetConfig):
    '''reloads revit links from a given location based on the original link type name (starts with)'''
    returnvalue = res.Result()
    try:
        # get all revit link types in model
        for p in FilteredElementCollector(doc).OfClass(RevitLinkType):
            linkTypeName = doSomethingWithLinkName(Element.Name.GetValue(p))
            newLinkPath = 'unknown'
            try:
                newLinkPath = GetLinkPath(linkTypeName, linkLocations, '.rvt')
                if(newLinkPath != None):
                    mp = ModelPathUtils.ConvertUserVisiblePathToModelPath(newLinkPath)
                    # attempt to reload with worksets set to last viewed
                    # wc = WorksetConfiguration(WorksetConfigurationOption.OpenLastViewed)
                    # however that can be achieved also ... According to Autodesk:
                    # If you want to load the same set of worksets the link previously had, leave this argument as a null reference ( Nothing in Visual Basic) .
                    wc = worksetConfig()
                    result = p.LoadFrom(mp,  wc)
                    # store result in message 
                    returnvalue.AppendMessage(linkTypeName + ' :: ' + str(result.LoadResult))
                else:
                    returnvalue.UpdateSep(False, linkTypeName + ' :: ' + 'No link path or multiple path found in provided locations')
            except Exception as e:
                returnvalue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnvalue

# link locations: a list of directories where the revit files can be located
# linkTypesTobReloaded is a list of elements of class RevitLinkType
# dosomethingwithLinkName can be used to truncate i.e. the revision details of a link
# worksetconfig: None: to use the previously apllied workset config
def ReloadRevitLinksFromList(doc, linkTypesTobReloaded, linkLocations, hostNameFormatted, doSomethingWithLinkName, worksetConfig):
    '''reloads revit links from a given location based on the original link type name (starts with)'''
    returnvalue = res.Result()
    try:
        # loop over links supplied
        for p in linkTypesTobReloaded:
            linkTypeName = doSomethingWithLinkName(Element.Name.GetValue(p))
            newLinkPath = 'unknown'
            try:
                newLinkPath = GetLinkPath(linkTypeName, linkLocations, '.rvt')
                if(newLinkPath != None):
                    mp = ModelPathUtils.ConvertUserVisiblePathToModelPath(newLinkPath)
                    # attempt to reload with worksets set to last viewed
                    # wc = WorksetConfiguration(WorksetConfigurationOption.OpenLastViewed)
                    # however that can be achieved also ... According to Autodesk:
                    # If you want to load the same set of worksets the link previously had, leave this argument as a null reference ( Nothing in Visual Basic) .
                    wc = worksetConfig()
                    result = p.LoadFrom(mp,  wc)
                    # store result in message 
                    returnvalue.AppendMessage(linkTypeName + ' :: ' + str(result.LoadResult))
                else:
                    returnvalue.UpdateSep(False, linkTypeName + ' :: ' + 'No link path or multiple path found in provided locations')
            except Exception as e:
                returnvalue.UpdateSep(False, linkTypeName + ' :: ' + 'Failed with exception: ' + str(e))
    except Exception as e:
        returnvalue.UpdateSep(False, 'Failed with exception: ' + str(e))
    return returnvalue

# returns None if multiple or no matches where found
def GetLinkPath(fileName, possibleLinkLocations, fileExtension):
    '''returns a fully qualified file path to a file name (revit project file extension .rvt) match in given directory locations'''
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

# which returns the name unchanged
# could be replaced with something which i.e. truncates the revision...
def DefaultLinkName(name):
    '''default 'do something with link name' method'''
    return name

# None in this case reloads a link with the last used workset settings
def DefaultWorksetConfigForReload():
    '''default method for returning a workset configuration'''
    return None

# ------------------------------------------------------- Revit link reporting --------------------------------------------------------------------

# doc:      current model document
# revitLinkType:    the revit link type element to get data from
def GetRevitLinkTypeData(doc, revitLinkType):
    '''returns Revit Link Type data for reporting'''
    # default values
    modelPath = 'unknown'
    isLoaded = False
    isFromLocalPath = False
    pathType = 'unknown'
    isLoaded = revitLinkType.IsLoaded(doc, revitLinkType.Id)
    isFromLocalPath = revitLinkType.IsFromLocalPath()
    exFileRef = revitLinkType.GetExternalFileReference()
    # get the workset of the link type (this can bew different to the workset of the link instance)
    wsparam = revitLinkType.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
    if(exFileRef.IsValidExternalFileReference(exFileRef)):
        modelPath = ModelPathUtils.ConvertModelPathToUserVisiblePath(exFileRef.GetPath())
        pathType = exFileRef.PathType.ToString()

    data=[
        Element.Name.GetValue(revitLinkType),
        str(isLoaded), 
        str(wsparam.AsValueString()), 
        str(isFromLocalPath), 
        pathType, 
        modelPath]
      
    return data

# doc:      current model document
# revitFilePath:    the revit host file path
def GetRevitLinkReportData(doc, revitFilePath):
    '''returns Revit Link data for reporting'''
    data = []
    collector = GetAllRevitLinkInstances(doc)
    for c in collector:
        # get the workset
        wsparam = c.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        # get the design option
        doparam = c.get_Parameter(BuiltInParameter.DESIGN_OPTION_ID)
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
        linkTypeData = [revitFilePath] + [str(c.Id)] + linkTypeData + [str(lS)] +[linkLocationName] + [com.getParameterValue(wsparam)] + [com.getParameterValue(doparam)]
        data.append(linkTypeData)
    return data
        
# -------------------------------------------- IMAGES -------------------------------------------------

# doc   current model document
def GetImagesTypesInModel(doc):
    '''returns all image link types and image link instances in a model'''
    collector = FilteredElementCollector(doc).OfClass(ImageType)
    return collector

def GetImagesTypeIdsInModel(doc):
    '''returns all image link type Ids and image link instance ids in a model'''
    ids = []
    col = GetImagesTypesInModel(doc)
    ids = com.GetIdsFromElementCollector(col)
    return ids

# doc   current model document
def SortImageLinkTypesByImportOrLinked(doc):
    '''returns two lists: First one: images linked into model, secon one images saved into model from model itself (no external file reference)'''
    imageLink = []
    imageImport = []
    collectorImageTypes = GetImagesTypesInModel(doc)
    for im in collectorImageTypes:
        if(im.IsLoadedFromFile()):
            imageLink.append(im)
        else:
            imageImport.append(im)
    return imageLink, imageImport

# doc   current model document
def GetAllImageLinkTypeLinkedInModel(doc):
    '''returns all image link types which are external referenced in a model'''
    imageLinks, imageImport = SortImageLinkTypesByImportOrLinked(doc)
    return imageLinks

# doc   current model document
def GetAllImageLinkTypeImportedInModel(doc):
    '''returns all iamge link types which are imported in a model'''
    imageLinks, imageImport = SortImageLinkTypesByImportOrLinked(doc)
    return imageImport

# doc   current model document
def GetImageTypeInModel(doc):
    '''returns all image types in a model'''
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RasterImages).WhereElementIsElementType()

# doc   current model document
def GetImageInstancesInModel(doc):
    '''returns all images placed in a model'''
    return FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RasterImages).WhereElementIsNotElementType()

# doc   current model document
def GetAllUnusedImagetypeIdsInModel(doc):
    '''returns all image types placed in a model'''
    unusedImages = com.GetNotPlacedTypes(doc, GetImageTypeInModel, GetImageInstancesInModel)
    unusedTypeIds = []
    for i in unusedImages:
        unusedTypeIds.append(i.Id)
    return unusedTypeIds

# doc   current model document
def GetAllUnusedImagetypeIdsInModelWithGroupCheck(doc):
    '''returns all image types placed in a model but includes group definition check
    this only returns valid data if at least one instance of the group is placed in the model!!
    otherwise images in groups which are not placed will not be flagged by this filter!'''
    unusedTypeIds = GetAllUnusedImagetypeIdsInModel(doc)
    # and filter by any type id's in groups which may not be placed and hence no instance present in the model
    unusedTypeIds = com.GetUnusedTypeIdsFromDetailGroups(doc, unusedTypeIds)
    return unusedTypeIds