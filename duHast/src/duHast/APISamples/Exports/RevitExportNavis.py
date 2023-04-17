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

from duHast.APISamples.Views import RevitViews as rView
from duHast.Utilities import Result as res
from duHast.APISamples.Exports.RevitExport import build_export_file_name_from_view


def setup_nwc_custom_export_option(usingSharedCoordinates, exportEntireModel, exportLinks, splitModelByLevel, exportParts, exportRoomAsAttributes, exportRoomGeometry, findMissingMaterials):
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


def setup_nwc_default_export_option_shared_by_view():
    '''
    Return an NWC Export Options object with shared coordinates, export by View.
    :return: A Navisworks .nwc export option.
    :rtype: Autodesk.Revit.DB.NavisworksExportOptions
    '''

    return setup_nwc_custom_export_option(True, False, False, True, True, False, False, False)

def export_to_nwc(doc, nwcExportOption, directoryPath, fileName):
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


def export_model_to_nwc(doc, nwcExportOption, directoryPath, fileName):
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
    returnValueByModel = export_to_nwc(doc, nwcExportOption, directoryPath, fileName)
    returnValue.Update(returnValueByModel)
    return returnValue


def export_3d_views_to_nwc(doc, viewFilter, nwcExportOption, directoryPath, doSomethingWithViewName = None):
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
    views = rView.get_views_of_type(doc, rdb.ViewType.ThreeD)
    for v in views:
        if(v.Name.lower().startswith(viewFilter.lower())):
            viewsToExport.append(v)
    # export those views one by one
    if(len(viewsToExport) > 0):
        for exportView in viewsToExport:
            returnValueByView = res.Result()
            # store view ID in export option
            nwcExportOption.ViewId = exportView.Id
            fileName = build_export_file_name_from_view(exportView.Name, viewFilter, '.nwc') if doSomethingWithViewName == None else doSomethingWithViewName(exportView.Name)
            returnValueByView = export_to_nwc(doc, nwcExportOption, directoryPath, fileName)
            returnValue.Update(returnValueByView)
    else:
        returnValue.UpdateSep(True, 'NWC Export: No 3D views found matching filter...nothing was exported')
    return returnValue