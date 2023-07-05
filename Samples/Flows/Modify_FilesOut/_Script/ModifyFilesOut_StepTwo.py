#!/usr/bin/python
# -*- coding: utf-8 -*-
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

# --------------------------
# Imports
# --------------------------
import clr

import settings as settings # sets up all commonly used variables and path locations!
import RevitExportIFCConfigSpecific as rexIFC
from utils import utils as utilLocal

# import common library
from duHast.APISamples import RevitCommonAPI as com
from duHast.Utilities.Objects import result as res
from duHast.APISamples import RevitExport as rex
from duHast.APISamples import RevitViews as rView
from duHast.Utilities import Utility as util
from duHast.Utilities import SolibriIFCOptimizer as sol

import Autodesk.Revit.DB as rdb

# flag whether this runs in debug or not
debug_ = False

# Add batch processor scripting references
if not debug_:
    import revit_script_util
    import revit_file_util
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
     # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    revit_file_path_ = revit_script_util.GetRevitFilePath()
else:
    #get default revit file name
    revit_file_path_ = settings.DEBUG_REVIT_FILE_NAME

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

# the revision of the current Revit model (as per splash screen)
current_file_revision_ = '-'
# store output here, using separate variable since its value is getting changed
root_path_ = settings.ROOT_PATH

def write_out_export_file_data(export_status, message, extension):
    if(export_status.status == True):
        if(export_status.result is not None and len(export_status.result)>0):
            for export_name in export_status.result:
                # strip extension of export file name
                export_file_name = export_name[1][0:-4]
                # get the file extension including .
                export_extension = export_name[1][-4:]
                data = get_file_data(export_file_name, extension)
                if(len(data)>0):
                    file_name = root_path_  + \
                        '\\' + export_file_name + \
                        export_extension + \
                        settings.MARKER_FILE_EXTENSION
                    status, message_marker = utilLocal.write_rev_marker_file(file_name, data)
                    Output(message_marker + ' :: ' + str(status))
                else:
                    Output('Failed to write marker file: No file data found for exported file: {}'.format(export_file_name))
        else:
            Output('Failed to write export marker files for: {}. No export file names provided'.format(message))
    else:
        Output('Failed to write export marker files for: {}. Export failed!'.format(message))

def get_file_data(export_file_name, extension):
    # get all file data with extension match
    return_value = []
    filtered_data = []
    for fd in file_data_:
        # Output ('File ex: '+str(fd.fileExtension)+ ' vs search ex: ' + extension)
        if (fd.fileExtension == extension):
            filtered_data.append(fd)
            # Output(fd)
    # flag: there are edge cases where the initial view name does not match the output file name
    # if flag is still false after first test...check the aconex doc number property for a match
    found_match = False
    for fdf in filtered_data:
        if (export_file_name.startswith(fdf.existingFileName)):
            # update revision to match revit file revision before writing out marker file
            fdf.revision = current_file_revision_
            return_value = fdf.getData()
            found_match = True
            break
    # check aconex doc number property in edge case...
    if (found_match == False):
        for fdf in filtered_data:
            if (export_file_name.startswith(fdf.AconexDocNumber)):
                # update revision to match revit file revision before writing out marker file
                fdf.revision = current_file_revision_
                return_value = fdf.getData()
                break
    return return_value

def build_default_file_list():
    flag = True
    # read current files
    file_list = utilLocal.read_current_file(settings.REVISION_DATA_FILEPATH)
    if(file_list is not None and len(file_list) > 0):
        # Output('got file data objects')
        for f in file_list:
            file_data_.append(f) # = fileList
    else:
        # Output('no file data objects returned')
        flag = False
    return flag

# optimizes ifc files after export
def optimize_ifc_files (export_status):
    return_value = res.Result()
    ifcFiles = []
    if(export_status.status == True):
        if(export_status.result is not None and len(export_status.result)>0):
            for export_name in export_status.result:
                # check if file exists...
                current_full_file_name = export_name[0] + '\\' + export_name[1]
                if(util.FileExist(current_full_file_name)):
                    ifcFiles.append(current_full_file_name)
                else:
                    return_value.AppendMessage('File not found: {}'.format(current_full_file_name))
            # start the optimization, save files in same directory
            ifc_optimize_status = sol.OptimizeIFCFilesInList(ifcFiles, root_path_)
            return_value.Update(ifc_optimize_status)
        else:
            return_value.UpdateSep(True, 'No IFC files optimized since nothing was exported')    
    else:
        return_value.UpdateSep(True, 'No IFC files optimized since nothing was exported')
    return return_value

# checks whether view names starts with ETN (navis) 00 STC and 99 STC (model start view)
def check_name(view):
    value = True
    for prefix in settings.VIEWS_TO_KEEP_FOR_EXPORT:
        if(view.Name.lower().startswith(prefix.lower())):
            value = False
            break
    return value

#----------------------------------export----------------------------------

def get_ifc_third_party_export_config(doc):
    '''
    Get's a custom IFC export config defined in module RevitExportIFCConfigSpecific

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: _description_
    :rtype: _type_
    '''

    return rexIFC.ifc_get_third_party_export_config_by_view_2022(doc)

def export_views_to_ifc(doc):
    '''
    Exports 3D views to ifc where the view name has a particular prefix.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: _description_
    :rtype: _type_
    '''

    return_value = res.Result()
    ifc_export_option = get_ifc_third_party_export_config(doc)
    #fileName = BuildExportFileNameIFC()
    return_value = rex.Export3DViewsToIFC(
        doc, 
        settings.EXPORT_IFC_VIEW_PREFIX, 
        ifc_export_option, 
        root_path_, 
        rex.IFCCoords.SharedCoordinates, 
        build_export_file_name_from_view_ifc
    )
    #returnvalue = rex.ExportModelToIFC(doc, ifcExportOption, rootPath_, fileName, rex.IFCCoords.SharedCoordinates)
    return return_value

def build_export_file_name_from_view_ifc(view_name):
    '''
    Creates the ifc file name based on the view the file gets exported from.

    - Includes revision information
    - If view starts with predefined Prefix, that prefix will be removed from the name

    :param view_name: The view name.
    :type view_name: str

    :return: The file name based on the view name.
    :rtype: str
    '''

    # return newFileName
    if(view_name.startswith(settings.EXPORT_IFC_VIEW_PREFIX)):
        lenPrefix = len(settings.EXPORT_IFC_VIEW_PREFIX)
        view_name = view_name[lenPrefix:]

        # this is required since the view name does not match the file name required at end of export
        for fd in file_data_:
            if(fd.existingFileName == view_name and fd.fileExtension == settings.IFC_FILE_EXTENSION):
                # may need to update the revision info!
                if(settings.EXPORT_FILES_USE_REVIT_REVISION):
                    Output('IFC using sheet revision: {}'.format(current_file_revision_))
                    # update the revision to the current revit file revision
                    fd.revision = current_file_revision_
                else:
                    # increase rev counter for this file
                    fd.upDateNumericalRev()
                    Output('IFC Numerical + 1 revision: {}'.format(fd.getNewFileName()))
                view_name = fd.getNewFileName()
                Output('IFC: view name new: {}'.format(view_name))
                break
            
    return view_name + settings.IFC_FILE_EXTENSION

def set_up_nwc_default_export_option():
    '''
    Return an NWC Export Options object with shared coordinates, export by View as provided in the generic library

    :return: _description_
    :rtype: _type_
    '''
    return rex.SetUpNWCDefaultExportOptionSharedByView()

def export_views_to_nwc(doc):
    '''
    Exports 3D views to nwc where the view name has a particular prefix.

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: _description_
    :rtype: _type_
    '''

    return_value = res.Result()
    nwc_export_option = set_up_nwc_default_export_option()
    return_value = rex.Export3DViewsToNWC(doc, settings.EXPORT_NWC_VIEW_PREFIX, nwc_export_option,  root_path_, build_export_file_name_from_view_nwc)
    return return_value

def build_export_file_name_from_view_nwc(view_name):
    '''
    Creates the nwc file name based on the view the file gets exported from.

    - Includes revision information
    - If view starts with predefined Prefix, that prefix will be removed from the name

    :param view_name: The view name.
    :type view_name: str

    :return: The file name based on the view name.
    :rtype: str
    '''

    len_prefix = len(settings.EXPORT_NWC_VIEW_PREFIX)
    #check if view name starts with NWC_
    if(view_name.startswith(settings.EXPORT_NWC_VIEW_PREFIX)):
        view_name = view_name[len_prefix:]
        # this is required since the view name does not match the file name required at end of export
        for fd in file_data_:
            if(fd.existingFileName == view_name and fd.fileExtension == settings.NWC_FILE_EXTENSION):
                # may need to update the revision info!
                if(settings.EXPORT_FILES_USE_REVIT_REVISION):
                    # update the revision to the current revit file revision
                    fd.revision = current_file_revision_
                else:
                    # increase rev coounter for this file
                    fd.upDateNumericalRev()
                view_name = fd.getNewFileName()
                break
    return view_name + settings.NWC_FILE_EXTENSION

# -------------
# main:
# -------------

# list containing the default file names:
# [[revit host file name before save, revit host file name after save]]
defaultFileNamesStepTwo_ = [
    [util.GetFileNameWithoutExt(revit_file_path_), str(util.GetFolderDateStamp(util.FOLDER_DATE_STAMP_YYMMDD)) + settings.REVIT_FILE_NAME_PREFIX_EXPORT + str(util.GetFileNameWithoutExt(revit_file_path_))]
]

# save revit file to new location
Output('Modifying Revit File.... start')

# array to contain file information read from text file
file_data_ = []

# set path to models will be saved to
root_path_ = root_path_ + '\\' + settings.MODEL_OUT_FOLDER_NAME
# get the current model revision recorded on sheet splash screen
current_file_revision_ = com.GetSheetRevByName(doc, settings.SPLASH_SCREEN_SHEET_NAME)
# the current file name
revitFileName_ = util.GetFileNameWithoutExt(revit_file_path_)

# read default file list info
build_default_file_list()

# just check for debug flag
if (debug_ == False):
    result_ = com.SaveAs(doc, settings.ROOT_PATH_EXPORT , revit_file_path_, defaultFileNamesStepTwo_)
    Output('{} :: [{}]'.format(result_.message,result_.status))

    # delete all sheets left in model
    resultDeleteAllSheets_ = rView.DeleteAllSheetsInModel(doc)
    Output('{} :: [{}]'.format(resultDeleteAllSheets_.message, resultDeleteAllSheets_.status))
    
    # delete views not on sheets
    resultDeleteViewsNotOnSheets_ = rView.DeleteViewsNotOnSheets(doc, check_name)
    Output('{} :: [{}]'.format(resultDeleteViewsNotOnSheets_.message, resultDeleteViewsNotOnSheets_.status))

    # export to IFC...
    Output('Exporting.... start')

    # export to NWC...
    flagExportNWC_ = export_views_to_nwc(doc)
    Output('{} :: [{}]'.format(flagExportNWC_.message, flagExportNWC_.status))
    write_out_export_file_data(flagExportNWC_, 'NWC Export', settings.NWC_FILE_EXTENSION)
    
    # export to IFC file format
    flagExportIFC_ = export_views_to_ifc(doc)
    Output('{} :: [{}]'.format(flagExportIFC_.message, flagExportIFC_.status))
    write_out_export_file_data(flagExportIFC_, 'IFC export', settings.IFC_FILE_EXTENSION)
    
    # duplicate NWC's
    flagCopyNWCs_ = utilLocal.copy_exports(flagExportNWC_, settings.ROOT_PATH_NWC, settings.NWC_FILE_EXTENSION)
    Output('{} :: [{}]'.format(flagCopyNWCs_.message, flagCopyNWCs_.status))
    
    # optimize IFC's prior to copying
    flagIFCOptimized_ = optimize_ifc_files (flagExportIFC_)
    Output('{} :: [{}]'.format(flagIFCOptimized_.message, flagIFCOptimized_.status))

    # duplicate IFC's
    flagCopyIFCs_ = utilLocal.copy_exports(flagExportIFC_, settings.ROOT_PATH_IFC, settings.IFC_FILE_EXTENSION)
    Output('{} :: [{}]'.format(flagCopyIFCs_.message, flagCopyIFCs_.status))
    
     # set up BIM 360 NWC folder
    setUpBIM360FolderFlag_ = utilLocal.create_bim360_out_folder(root_path_)
    if(setUpBIM360FolderFlag_):
        nwcExportPath = root_path_ + '\\' + settings.BIM360_FOLDER_NAME
        # duplicate NWC's
        flagCopyNWCs_ = utilLocal.copy_exports(flagExportNWC_, nwcExportPath, settings.NWC_FILE_EXTENSION)
        Output('{} :: [{}]'.format(flagCopyNWCs_.message, flagCopyNWCs_.status))
    else:
        Output('failed to set up BIM 360 out folder')

else:
    Output('Debug mode!!!')

Output('Modifying Revit File.... finished ')