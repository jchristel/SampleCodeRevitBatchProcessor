'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around exporting from Revit to varies file formats.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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
import sys

# custom result class
from duHast.Utilities import Result as res

from System.IO import Path
import Autodesk.Revit.DB as rdb

# import common library
from duHast.APISamples import RevitTransaction as rTran
from duHast.APISamples import RevitViews as rView
# this imports 3rd party ifc exporters depending on version of Revit in use.
from duHast.APISamples import RevitExportIFCConfig as ifcCon

#-------------------------------------------- IFC EXPORT 3rd Party -------------------------------------


class IFCCoords:
    '''
    Using enum class for IFC coordinates options.
    '''
    SharedCoordinates = '0'
    SiteSurveyPoint = '1'
    ProjectBasePoint = '2'
    InternalCoordinates = '3'
    ProjectInTN = '4',
    InternalInTN = '5'

class IFCSpaceBoundaries:
    '''
    Using enum class for IFC space boundary options.
    '''
    noBoundaries = 0
    firstLevel = 1
    secondLevel = 2

def ExportToIFC(doc, ifcExportOption, directoryPath, fileName):
    '''
    Exports to IFC either the entire model or a view only using 3rd party exporter.

    What gets exported is defined in the ifcExportOption.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ifcExportOption: The settings for the IFC export.
    :type ifcExportOption: BIM.IFC.Export.UI.IFCExportConfiguration
    :param directoryPath: The directory path to where the export is being saved.
    :type directoryPath: str
    :param fileName: The file name under which the export is being saved.
    :type fileName: str
    :return: 
        Result class instance.

        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path of the exported file.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    # ifc export needs to run in a transaction
    returnValue = res.Result()
    def action():
        actionReturnValue = res.Result()
        try:
            # export to IFC
            doc.Export(directoryPath, fileName, ifcExportOption)
            actionReturnValue.UpdateSep(True, 'Exported: ' + str(directoryPath) + '\\' + str(fileName))
            # needs to be a list in a list to stay together when combined with previous results in the update status result code
            actionReturnValue.result = [[directoryPath, fileName]]
        except Exception as e:
            actionReturnValue.UpdateSep(False, 'Script Exception: Failed to export to IFC with exception: ' + str(e))
        return actionReturnValue
    transaction = rdb.Transaction(doc,'Export to IFC')
    returnValue = rTran.in_transaction(transaction, action)
    return returnValue

def IFCGetThirdPartyExportConfigByView(doc, ifcVersion, ifcSettings = None):
    '''
    Returns the 3rd party ifc config for export by view depending on revit version.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ifcVersion: The ifc version used for the export.
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :raises ValueError: Raises an exception if the revit version in use is not supported by this script.
    
    :return: An ifc export config instance based on the Revit version.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # get the revit version:
    revitVersion = doc.Application.VersionNumber
    ifcConfig = None
    if (revitVersion == '2019'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByView2019(ifcVersion, ifcSettings)
    elif (revitVersion == '2020'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByView2020(ifcVersion, ifcSettings)
    elif (revitVersion == '2021'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByView2021(ifcVersion, ifcSettings)
    elif (revitVersion == '2022'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByView2022(ifcVersion, ifcSettings)
    else:
        # this is a non supported revit version!
        raise ValueError('Revit version ' + revitVersion + ' is currently not supported by IFC exporter!')
    return ifcConfig

def IFCGetThirdPartyExportConfigByModel(doc, ifcVersion, ifcSettings = None):
    '''
    Returns the 3rd party ifc config for export by model depending on revit version.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ifcVersion: The ifc version used for the export.
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :raises ValueError: Raises an exception if the revit version in use is not supported by this script.
    
    :return: An ifc export config instance based on the Revit version.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    # get the revit version:
    revitVersion = doc.Application.VersionNumber
    ifcConfig = None
    if (revitVersion == '2019'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByModel2019(ifcVersion, ifcSettings)
    elif (revitVersion == '2020'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByModel2020(ifcVersion, ifcSettings)
    elif (revitVersion == '2021'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByModel2021(ifcVersion, ifcSettings)
    elif (revitVersion == '2022'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByModel2022(ifcVersion, ifcSettings)
    else:
        # this is a non supported revit version!
        raise ValueError('Revit version ' + revitVersion + ' is currently not supported by IFC exporter!')
    return ifcConfig

def SetUpIFCExportOption(exportConfig, viewId = rdb.ElementId.InvalidElementId, coordOption = IFCCoords.SharedCoordinates):
    '''
    Function assigning a view Id to export ifc config if it is exporting by view.

    By model export will assign Autodesk.Revit.DB.ElementId.InvalidElementId instead.

    :param exportConfig: The ifc export configuration used.
    :type exportConfig: BIM.IFC.Export.UI.IFCExportConfiguration
    :param viewId: The id of the view to be exported, defaults to ElementId.InvalidElementId
    :type viewId: Autodesk.Revit.DB.ElementId, optional
    :param coordOption: Describes the coordinate options used for the export, defaults to IFCCoords.SharedCoordinates
    :type coordOption: SampleCodeBatchProcessor.RevitExport.IFCCoords, optional
    
    :return: An updated ifc export config instance.
    :rtype: BIM.IFC.Export.UI.IFCExportConfiguration
    '''

    if(exportConfig.UseActiveViewGeometry == True):
        exportConfig.ActiveViewId = viewId.IntegerValue
    else:
        exportConfig.ActiveViewId = -1
    # set up the ifc export options object
    exIFC = rdb.IFCExportOptions()
    exportConfig.UpdateOptions(exIFC, viewId)

    # set the coordinate system to use
    exIFC.AddOption('SitePlacement', coordOption)

    return exIFC

def ExportModelToIFC(doc, ifcExportOption, directoryPath, fileName, coordOption = IFCCoords.SharedCoordinates):
    '''
    Function exporting the entire model to IFC using 3rd party exporter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param ifcExportOption: The IFC export option.
    :type ifcExportOption: Autodesk.Revit.DB.IFCExportOptions
    :param directoryPath: The directory path to where the export is being saved.
    :type directoryPath: str
    :param fileName: The file name under which the export is being saved.
    :type fileName: str
    :param coordOption: Describes the coordinate options used for the export, defaults to IFCCoords.SharedCoordinates
    :type coordOption: SampleCodeBatchProcessor.RevitExport.IFCCoords, optional
    
    :return: 
        Result class instance.

        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path of the exported file.
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # need to create an export option from the export config
    exIFC = rdb.IFCExportOptions()
    # pass in invalid element ID to export entire model
    ifcExportOption.UpdateOptions(exIFC, rdb.ElementId.InvalidElementId)

    # set the coordinate system to use
    exIFC.AddOption('SitePlacement', coordOption)
    returnValueByModel = ExportToIFC(doc, exIFC, directoryPath, fileName)
    returnValue.Update(returnValueByModel)
    return returnValue

# 
# doSomethingWithViewName method will accept view name as arg only
def Export3DViewsToIFC(doc, viewFilter, ifcExportOption, directoryPath, ifcCoordinatesSystem = IFCCoords.SharedCoordinates, doSomethingWithViewName = None):
    '''
    Function exporting 3D views matching a filter (view starts with) to IFC using 3rd party exporter.

    By default the file name of the export will be same as the name of the view exported.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param viewFilter: String the view name is to start with if it is to be exported. (Both view name and string are set to lower at comparison)
    :type viewFilter: str
    :param ifcExportOption: The IFC export option.
    :type ifcExportOption: Autodesk.Revit.DB.IFCExportOptions
    :param directoryPath: The directory path to where the export is being saved.
    :type directoryPath: str
    :param ifcCoordinatesSystem: Describes the coordinate options used for the export, defaults to IFCCoords.SharedCoordinates
    :type ifcCoordinatesSystem: SampleCodeBatchProcessor.RevitExport.IFCCoords, optional
    :param doSomethingWithViewName: A function which takes as an argument the view name and does something with it. The modified view name is afterwards used as the actual file name, defaults to None which uses the view name unchanged as the export file name.
    :type doSomethingWithViewName: function , optional
    
    :return: 
        Result class instance.

        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path of the exported file.
        
        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    viewsToExport = []
    # get all 3D views in model and filter out views to be exported
    views = rView.GetViewsOfType(doc, rdb.ViewType.ThreeD)
    for v in views:
        if(v.Name.lower().startswith(viewFilter.lower())):
            viewsToExport.append(v)
    # export those views one by one
    if(len(viewsToExport) > 0):
        for exportView in viewsToExport:
            returnValueByView = res.Result()
            updatedExportOption = SetUpIFCExportOption(ifcExportOption, exportView.Id, ifcCoordinatesSystem)
            fileName = BuildExportFileNameFromView(exportView.Name, viewFilter, '.ifc') if doSomethingWithViewName == None else doSomethingWithViewName(exportView.Name)
            returnValueByView = ExportToIFC(doc, updatedExportOption, directoryPath, fileName)
            returnValue.Update(returnValueByView)
    else:
        returnValue.UpdateSep(True, 'No 3D views found matching filter...nothing was exported')
    return returnValue

def BuildExportFileNameFromView(viewName, viewFilterRule, fileExtension):
    '''
    Function modifying the past in view name and returns a file name.

    :param viewName: The view name to be used as file name.
    :type viewName: str
    :param viewFilterRule: A prefix which will be removed from the view name.
    :type viewFilterRule: str
    :param fileExtension: The file extension to be used. Format is '.something'
    :type fileExtension: str
    :return: A file name.
    :rtype: str
    '''

    # check if file extension is not none
    if (fileExtension is None):
        fileExtension = '.tbc'
    # check the filter rule
    if (viewFilterRule is None):
        newFileName = viewName + fileExtension
    else:
        newFileName = viewName[len(viewFilterRule):] + fileExtension
        newFileName = newFileName.strip()
    return newFileName

#-------------------------------------------- IFC default -------------------------------------

def IFCGetExportConfigByView(ifcVersion, ifcSpaceBounds = IFCSpaceBoundaries.noBoundaries):
    '''
    Returns an IFC export configuration for the built in IFC exporter.

    :param ifcVersion: The ifc version used for the export.
    :type ifcVersion: Autodesk.Revit.DB.IFCVersion
    :param ifcSpaceBounds: IFC space boundary setting, defaults to IFCSpaceBoundaries.noBoundaries
    :type ifcSpaceBounds: SampleCodeBatchProcessor.RevitExport.IFCSpaceBoundaries, optional
    
    :return: an IFC export option
    :rtype: Autodesk.Revit.DB.IFCExportOptions
    '''

    exIFC = rdb.IFCExportOptions()
    exIFC.ExportBaseQuantities = True
    exIFC.FileVersion = ifcVersion
    exIFC.SpaceBoundaryLevel = ifcSpaceBounds
    exIFC.WallAndColumnSplitting = True
    return exIFC

def Export3DViewsToIFCDefault(doc, viewFilter, ifcExportOption, directoryPath):
    '''
    Exports 3D views matching a filter (view starts with) to IFC using the default built in exporter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param viewFilter: String the view name is to start with if it is to be exported. (Both view name and string are set to lower at comparison)
    :type viewFilter: str
    :param ifcExportOption: The IFC export option.
    :type ifcExportOption: Autodesk.Revit.DB.IFCExportOptions
    :param directoryPath: The directory path to where the export is being saved.
    :type directoryPath: str
    
    :return: 
        Result class instance.

        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path of the exported file.
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    viewsToExport = []
    # get all 3D views in model and filter out views to be exported
    views = rView.GetViewsOfType(doc, rdb.ViewType.ThreeD)
    for v in views:
        if(v.Name.lower().startswith(viewFilter.lower())):
            viewsToExport.append(v)
    # export those views one by one
    if(len(viewsToExport) > 0):
        for exportView in viewsToExport:
            returnValueByView = res.Result()
            ifcExportOption.FilterViewId = exportView.Id
            fileName = BuildExportFileNameFromView(exportView.Name, viewFilter, '.ifc')
            returnValueByView = ExportToIFC(doc, ifcExportOption, directoryPath, fileName)
            returnValue.Update(returnValueByView)
    else:
        returnValue.UpdateSep(True, 'No 3D views found matching filter...nothing was exported')
    return returnValue

#-------------------------------------------- NWC EXPORT -------------------------------------

def SetUpNWCDefaultExportOptionSharedByView():
    '''
    Return an NWC Export Options object with shared coordinates, export by View.

    :return: A Navisworks .nwc export option.
    :rtype: Autodesk.Revit.DB.NavisworksExportOptions
    '''
    
    return SetUpNWCCustomExportOption(True, False, False, True, True, False, False, False)

def SetUpNWCCustomExportOption(usingSharedCoordinates, exportEntireModel, exportLinks, splitModelByLevel, exportParts, exportRoomAsAttributes, exportRoomGeometry, findMissingMaterials):
    '''
    Return an NWC Export Options object as per values past oin.

    :param usingSharedCoordinates: True shared coordinates will be used, otherwise project internal
    :type usingSharedCoordinates: bool
    :param exportEntireModel: True entire model will be exported, otherwise specific view.
    :type exportEntireModel: bool
    :param exportLinks: True: Revit links will also be exported, otherwise not.
    :type exportLinks: bool
    :param splitModelByLevel: True: model elements will be split by level, otherwise not.
    :type splitModelByLevel: bool
    :param exportParts: True parts will be exported, otherwise not.
    :type exportParts: bool
    :param exportRoomAsAttributes: True room properties will be exported (can be slow!), otherwise not.
    :type exportRoomAsAttributes: bool
    :param exportRoomGeometry: True room geometry will be exported, otherwise not.
    :type exportRoomGeometry: bool
    :param findMissingMaterials: True exporter will attempt to find missing materials, otherwise not
    :type findMissingMaterials: bool

    :return: A Navisworks .nwc export option.
    :rtype: Autodesk.Revit.DB.NavisworksExportOptions
    '''

    exNWC = rdb.NavisworksExportOptions()
    exNWC.Coordinates = rdb.NavisworksCoordinates.Shared if usingSharedCoordinates == True else rdb.NavisworksCoordinates.Internal
    exNWC.ExportScope = rdb.NavisworksExportScope.Model if exportEntireModel == True else rdb.NavisworksExportScope.View
    exNWC.ExportLinks = exportLinks
    exNWC.DivideFileIntoLevels = splitModelByLevel
    exNWC.ExportParts =  exportParts
    exNWC.ExportRoomAsAttribute = exportRoomAsAttributes
    exNWC.ExportRoomGeometry = exportRoomGeometry
    exNWC.FindMissingMaterials = findMissingMaterials
    exNWC.ConvertElementProperties = False
    
    return exNWC

def ExportToNWC(doc, nwcExportOption, directoryPath, fileName):
    '''
    Function exporting either entire model or view to NWC

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param nwcExportOption: A Navisworks .nwc export option.
    :type nwcExportOption: Autodesk.Revit.DB.NavisworksExportOptions
    :param directoryPath: The directory path to where the export is being saved.
    :type directoryPath: str
    :param fileName: The file name under which the export is being saved.
    :type fileName: str
    :return: 
        Result class instance.

        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path of the exported file.
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    # nwc export does not need to run in a transaction
    returnValue = res.Result()
    try:
        # export to NWC
        doc.Export(directoryPath, fileName, nwcExportOption)
        returnValue.UpdateSep(True, 'Exported: ' + str(directoryPath) + '\\' + str(fileName))
        # needs to be a list in a list to stay together when combined with previous results in the update status result code
        returnValue.result = [[directoryPath, fileName]]
    except Exception as e:
        returnValue.UpdateSep(False, 'Script Exception: Failed to export to NWC with exception: ' + str(e))
    return returnValue

def ExportModelToNWC(doc, nwcExportOption, directoryPath, fileName):
    '''
    Function exporting the entire model to NWC.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param nwcExportOption: A Navisworks .nwc export option.
    :type nwcExportOption: Autodesk.Revit.DB.NavisworksExportOptions
    :param directoryPath: The directory path to where the export is being saved.
    :type directoryPath: str
    :param fileName: The file name under which the export is being saved.
    :type fileName: str
    
    :return: 
        Result class instance.

        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path of the exported file.
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    returnValueByModel = ExportToNWC(doc, nwcExportOption, directoryPath, fileName)
    returnValue.Update(returnValueByModel)
    return returnValue

def Export3DViewsToNWC(doc, viewFilter, nwcExportOption, directoryPath, doSomethingWithViewName = None):
    '''
    Function exporting 3D views matching a filter (view starts with) to NWC.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param viewFilter: String the view name is to start with if it is to be exported. (Both view name and string are set to lower at comparison)
    :type viewFilter: str
    :param nwcExportOption: A Navisworks .nwc export option.
    :type nwcExportOption: Autodesk.Revit.DB.NavisworksExportOptions
    :param directoryPath: The directory path to where the export is being saved.
    :type directoryPath: str
    :param doSomethingWithViewName: A function which takes as an argument the view name and does something with it. The modified view name is afterwards used as the actual file name, defaults to None which uses the view name unchanged as the export file name.
    :type doSomethingWithViewName: function , optional
    
    :return: 
        Result class instance.

        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path of the exported file.
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
        
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    viewsToExport = []
    # get all 3D views in model and filter out views to be exported
    views = rView.GetViewsOfType(doc, rdb.ViewType.ThreeD)
    for v in views:
        if(v.Name.lower().startswith(viewFilter.lower())):
            viewsToExport.append(v)
    # export those views one by one
    if(len(viewsToExport) > 0):
        for exportView in viewsToExport:
            returnValueByView = res.Result()
            # store view ID in export option
            nwcExportOption.ViewId = exportView.Id
            fileName = BuildExportFileNameFromView(exportView.Name, viewFilter, '.nwc') if doSomethingWithViewName == None else doSomethingWithViewName(exportView.Name)
            returnValueByView = ExportToNWC(doc, nwcExportOption, directoryPath, fileName)
            returnValue.Update(returnValueByView)
    else:
        returnValue.UpdateSep(True, 'NWC Export: No 3D views found matching filter...nothing was exported')
    return returnValue
