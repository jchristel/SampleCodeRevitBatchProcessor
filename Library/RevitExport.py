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

clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)

# custom result class
import Result as res

from System.IO import Path
from Autodesk.Revit.DB import *

# import common library
import RevitCommonAPI as com
import RevitViews as rView
import RevitExportIFCConfig as ifcCon

#-------------------------------------------- IFC EXPORT 3rd Party -------------------------------------

# Using enum class for IFC coordinates options
class IFCCoords:
    SharedCoordinates = '0'
    SiteSurveyPoint = '1'
    ProjectBasePoint = '2'
    InternalCoordinates = '3'

class IFCSpaceBoundaries:
    noBoundaries = 0
    firstLevel = 1
    secondLevel = 2

# method exporting either entire model or view to IFC
def ExportToIFC(doc, ifcExportOption, directoryPath, fileName):
    # ifc export needs to run in a transaction
    returnvalue = res.Result()
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
    transaction = Transaction(doc,'Export to IFC')
    returnvalue = com.InTransaction(transaction, action)
    return returnvalue

# doc               current model document
# ifc version       ifc version used for export
def IFCGetThirdPartyExportConfigByView(doc, ifcVersion):
    '''returns the 3rd party ifc config for export by view depending on revit version'''
    # get the revit version:
    revitVersion = doc.Application.VersionNumber
    ifcConfig = None
    if (revitVersion == '2019'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByView2019(ifcVersion)
    elif (revitVersion == '2020'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByView2020(ifcVersion)
    elif (revitVersion == '2021'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByView2019(ifcVersion)
    elif (revitVersion == '2022'):
        pass
    else:
        # this is a non supported revit version!
        raise ValueError('Revit version ' + revitVersion + ' is currently not supported by IFC exporter!')
    return ifcConfig

# doc               current model document
# ifc version       ifc version used for export
def IFCGetThirdPartyExportConfigByModel(doc, ifcVersion):
    '''returns the 3rd party ifc config for export by model depending on revit version'''
    # get the revit version:
    revitVersion = doc.Application.VersionNumber
    ifcConfig = None
    if (revitVersion == '2019'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByModel2019(ifcVersion)
    elif (revitVersion == '2020'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByModel2020(ifcVersion)
    elif (revitVersion == '2021'):
        ifcConfig = ifcCon.IFCGetThirdPartyExportConfigByModel2021(ifcVersion)
    elif (revitVersion == '2022'):
        raise ValueError('Revit version ' + revitVersion + ' is currently not supported by IFC exporter!')
    else:
        # this is a non supported revit version!
        raise ValueError('Revit version ' + revitVersion + ' is currently not supported by IFC exporter!')
    return ifcConfig

# method assigning view Id to active export config if it is exporting by view
# and returning an IFCExportOptions object
def SetUpIFCExportOption(exportConfig, viewId = ElementId.InvalidElementId, coordOption = IFCCoords.SharedCoordinates):
    if(exportConfig.UseActiveViewGeometry == True):
        exportConfig.ActiveViewId = viewId.IntegerValue
    else:
        exportConfig.ActiveViewId = -1
    # set up the ifc export options object
    exIFC = IFCExportOptions()
    exportConfig.UpdateOptions(exIFC, viewId)

    # set the coordinate system to use
    exIFC.AddOption('SitePlacement', coordOption)

    return exIFC

# method exporting the entire model to IFC
def ExportModelToIFC(doc, ifcExportOption, directoryPath, fileName, coordOption = IFCCoords.SharedCoordinates):
    returnvalue = res.Result()
    # need to create an export option from the export config
    exIFC = IFCExportOptions()
    # pass in invalid element ID to export entire model
    ifcExportOption.UpdateOptions(exIFC, ElementId.InvalidElementId)

    # set the coordinate system to use
    exIFC.AddOption('SitePlacement', coordOption)
    returnvalueByModel = ExportToIFC(doc, exIFC, directoryPath, fileName)
    returnvalue.Update(returnvalueByModel)
    return returnvalue

# method exporting 3D views matching a filter (view starts with) to IFC
# doSomethingWithViewName method will accept view name as arg only
def Export3DViewsToIFC(doc, viewFilter, ifcExportOption, directoryPath, ifcCoordinatesSystem = IFCCoords.SharedCoordinates, doSomethingWithViewName = None):
    returnvalue = res.Result()
    viewsToExport = []
    # get all 3D views in model and filter out views to be exported
    views = rView.GetViewsofType(doc, ViewType.ThreeD)
    for v in views:
        if(v.Name.lower().startswith(viewFilter.lower())):
            viewsToExport.append(v)
    # export those views one by one
    if(len(viewsToExport) > 0):
        for exportView in viewsToExport:
            returnvalueByView = res.Result()
            updatedExportOption = SetUpIFCExportOption(ifcExportOption, exportView.Id, ifcCoordinatesSystem)
            fileName = BuildExportFileNameFromView(exportView.Name, viewFilter, '.ifc') if doSomethingWithViewName == None else doSomethingWithViewName(exportView.Name)
            returnvalueByView = ExportToIFC(doc, updatedExportOption, directoryPath, fileName)
            returnvalue.Update(returnvalueByView)
    else:
        returnvalue.UpdateSep(True, 'No 3D views found matching filter...nothing was exported')
    return returnvalue

def BuildExportFileNameFromView(viewName, viewFilterRule, fileExtension):
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

# Revit build in IFC export options
def IFCGetExportConfifgByView(ifcVersion, ifcSpaceBounds = IFCSpaceBoundaries.noBoundaries):
    exIFC = IFCExportOptions()
    exIFC.ExportBaseQuantities = True
    exIFC.FileVersion = ifcVersion
    exIFC.SpaceBoundaryLevel = ifcSpaceBounds
    exIFC.WallAndColumnSplitting = True
    return exIFC

# method exporting 3D views matching a filter (view starts with) to IFC using the default built in exporter
def Export3DViewsToIFCDefault(doc, viewFilter, ifcExportOption, directoryPath):
    returnvalue = res.Result()
    viewsToExport = []
    # get all 3D views in model and filter out views to be exported
    views = rView.GetViewsofType(doc, ViewType.ThreeD)
    for v in views:
        if(v.Name.lower().startswith(viewFilter.lower())):
            viewsToExport.append(v)
    # export those views one by one
    if(len(viewsToExport) > 0):
        for exportView in viewsToExport:
            returnvalueByView = res.Result()
            ifcExportOption.FilterViewId = exportView.Id
            fileName = BuildExportFileNameFromView(exportView.Name, viewFilter, '.ifc')
            returnvalueByView = ExportToIFC(doc, ifcExportOption, directoryPath, fileName)
            returnvalue.Update(returnvalueByView)
    else:
        returnvalue.UpdateSep(True, 'No 3D views found matching filter...nothing was exported')
    return returnvalue

#-------------------------------------------- NWC EXPORT -------------------------------------

# Return an NWC Export Options object with shared coordinates, export by View
def SetUpNWCDefaultExportOptionSharedByView():
    return SetUpNWCCustomExportOption(True, False, False, True, True, False, False, False)

# Return an NWC Export Options object 
def SetUpNWCCustomExportOption(usingSharedCoordinates, exportEntireModel, exportLinks, splitModelByLevel, exportParts, exportRoomAsAttributes, exportRoomGeometry, findMissingMaterials):
    exNWC = NavisworksExportOptions()
    exNWC.Coordinates = NavisworksCoordinates.Shared if usingSharedCoordinates == True else NavisworksCoordinates.Internal
    exNWC.ExportScope = NavisworksExportScope.Model if exportEntireModel == True else NavisworksExportScope.View
    exNWC.ExportLinks = exportLinks
    exNWC.DivideFileIntoLevels = splitModelByLevel
    exNWC.ExportParts =  exportParts
    exNWC.ExportRoomAsAttribute = exportRoomAsAttributes
    exNWC.ExportRoomGeometry = exportRoomGeometry
    exNWC.FindMissingMaterials = findMissingMaterials
    exNWC.ConvertElementProperties = False
    
    return exNWC

# method exporting either entire model or view to NWC
def ExportToNWC(doc, nwcExportOption, directoryPath, fileName):
    # nwc export does not need to run in a transaction
    returnvalue = res.Result()
    try:
        # export to NWC
        doc.Export(directoryPath, fileName, nwcExportOption)
        returnvalue.UpdateSep(True, 'Exported: ' + str(directoryPath) + '\\' + str(fileName))
        # needs to be a list in a list to stay together when combined with previous results in the update status result code
        returnvalue.result = [[directoryPath, fileName]]
    except Exception as e:
        returnvalue.UpdateSep(False, 'Script Exception: Failed to export to NWC with exception: ' + str(e))
    return returnvalue

# method exporting the entire model to NWC
def ExportModelToNWC(doc, nwcExportOption, directoryPath, fileName):
    returnvalue = res.Result()
    returnvalueByModel = ExportToNWC(doc, nwcExportOption, directoryPath, fileName)
    returnvalue.Update(returnvalueByModel)
    return returnvalue

# method exporting 3D views matching a filter (view starts with) to NWC
# doSomethingWithViewName method will accept view name as arg only
def Export3DViewsToNWC(doc, viewFilter, nwcExportOption, directoryPath, doSomethingWithViewName = None):
    returnvalue = res.Result()
    viewsToExport = []
    # get all 3D views in model and filter out views to be exported
    views = rView.GetViewsofType(doc, ViewType.ThreeD)
    for v in views:
        if(v.Name.lower().startswith(viewFilter.lower())):
            viewsToExport.append(v)
    # export those views one by one
    if(len(viewsToExport) > 0):
        for exportView in viewsToExport:
            returnvalueByView = res.Result()
            # store view ID in export option
            nwcExportOption.ViewId = exportView.Id
            fileName = BuildExportFileNameFromView(exportView.Name, viewFilter, '.nwc') if doSomethingWithViewName == None else doSomethingWithViewName(exportView.Name)
            returnvalueByView = ExportToNWC(doc, nwcExportOption, directoryPath, fileName)
            returnvalue.Update(returnvalueByView)
    else:
        returnvalue.UpdateSep(True, 'NWC Export: No 3D views found matching filter...nothing was exported')
    return returnvalue