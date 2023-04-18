'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around exporting from Revit to nwc file format.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.APISamples.Common import RevitTransaction as rTran
from duHast.Utilities import Result as res
from duHast.APISamples.Views import RevitViews as rView
from duHast.APISamples.Exports import RevitExportIFCConfig as ifcCon
from duHast.APISamples.Exports.RevitExport import build_export_file_name_from_view
from duHast.APISamples.Exports.Utility.IFCCoordinates import IFCCoords
from duHast.APISamples.Exports.Utility.IFCSpaceBoundaries import IFCSpaceBoundaries


def ifc_get_export_config_by_view(ifcVersion, ifcSpaceBounds = IFCSpaceBoundaries.no_boundaries):
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


def export_to_ifc(doc, ifcExportOption, directoryPath, fileName):
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
            actionReturnValue.update_sep(True, 'Exported: ' + str(directoryPath) + '\\' + str(fileName))
            # needs to be a list in a list to stay together when combined with previous results in the update status result code
            actionReturnValue.result = [[directoryPath, fileName]]
        except Exception as e:
            actionReturnValue.update_sep(False, 'Script Exception: Failed to export to IFC with exception: ' + str(e))
        return actionReturnValue
    transaction = rdb.Transaction(doc,'Export to IFC')
    returnValue = rTran.in_transaction(transaction, action)
    return returnValue


def export_3d_views_to_ifc_default(doc, viewFilter, ifcExportOption, directoryPath):
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
    views = rView.get_views_of_type(doc, rdb.ViewType.ThreeD)
    for v in views:
        if(v.Name.lower().startswith(viewFilter.lower())):
            viewsToExport.append(v)
    # export those views one by one
    if(len(viewsToExport) > 0):
        for exportView in viewsToExport:
            returnValueByView = res.Result()
            ifcExportOption.FilterViewId = exportView.Id
            fileName = build_export_file_name_from_view(exportView.Name, viewFilter, '.ifc')
            returnValueByView = export_to_ifc(doc, ifcExportOption, directoryPath, fileName)
            returnValue.update(returnValueByView)
    else:
        returnValue.update_sep(True, 'No 3D views found matching filter...nothing was exported')
    return returnValue


def setup_ifc_export_option(exportConfig, viewId = rdb.ElementId.InvalidElementId, coordOption = IFCCoords.shared_coordinates):
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


def export_3d_views_to_ifc(doc, viewFilter, ifcExportOption, directoryPath, ifcCoordinatesSystem = IFCCoords.shared_coordinates, doSomethingWithViewName = None):
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
    views = rView.get_views_of_type(doc, rdb.ViewType.ThreeD)
    for v in views:
        if(v.Name.lower().startswith(viewFilter.lower())):
            viewsToExport.append(v)
    # export those views one by one
    if(len(viewsToExport) > 0):
        for exportView in viewsToExport:
            returnValueByView = res.Result()
            updatedExportOption = setup_ifc_export_option(ifcExportOption, exportView.Id, ifcCoordinatesSystem)
            fileName = build_export_file_name_from_view(exportView.Name, viewFilter, '.ifc') if doSomethingWithViewName == None else doSomethingWithViewName(exportView.Name)
            returnValueByView = export_to_ifc(doc, updatedExportOption, directoryPath, fileName)
            returnValue.update(returnValueByView)
    else:
        returnValue.update_sep(True, 'No 3D views found matching filter...nothing was exported')
    return returnValue


def export_model_to_ifc(doc, ifcExportOption, directoryPath, fileName, coordOption = IFCCoords.shared_coordinates):
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
    returnValueByModel = export_to_ifc(doc, exIFC, directoryPath, fileName)
    returnValue.update(returnValueByModel)
    return returnValue


def ifc_get_third_party_export_config_by_model(doc, ifcVersion, ifcSettings = None):
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
        ifcConfig = ifcCon.ifc_get_third_party_export_config_by_model_2019(ifcVersion, ifcSettings)
    elif (revitVersion == '2020'):
        ifcConfig = ifcCon.ifc_get_third_party_export_config_by_model_2020(ifcVersion, ifcSettings)
    elif (revitVersion == '2021'):
        ifcConfig = ifcCon.ifc_get_third_party_export_config_by_model_2021(ifcVersion, ifcSettings)
    elif (revitVersion == '2022'):
        ifcConfig = ifcCon.ifc_get_third_party_export_config_by_model_2022(ifcVersion, ifcSettings)
    else:
        # this is a non supported revit version!
        raise ValueError('Revit version ' + revitVersion + ' is currently not supported by IFC exporter!')
    return ifcConfig


def ifc_get_third_party_export_config_by_view(doc, ifcVersion, ifcSettings = None):
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
        ifcConfig = ifcCon.ifc_get_third_party_export_config_by_view_2019(ifcVersion, ifcSettings)
    elif (revitVersion == '2020'):
        ifcConfig = ifcCon.ifc_get_third_party_export_config_by_view_2020(ifcVersion, ifcSettings)
    elif (revitVersion == '2021'):
        ifcConfig = ifcCon.ifc_get_third_party_export_config_by_view_2021(ifcVersion, ifcSettings)
    elif (revitVersion == '2022'):
        ifcConfig = ifcCon.ifc_get_third_party_export_config_by_view_2022(ifcVersion, ifcSettings)
    else:
        # this is a non supported revit version!
        raise ValueError('Revit version ' + revitVersion + ' is currently not supported by IFC exporter!')
    return ifcConfig