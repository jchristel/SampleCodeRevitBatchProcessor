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
#

# --------------------------
# Imports
# --------------------------

import clr

import utilModifyBVN as utilM  # sets up all commonly used variables and path locations!
import utils as utilLocal

# import common library
from duHast.APISamples import RevitCommonAPI as com
from duHast.APISamples import RevitViews as rView
from duHast.APISamples import RevitLinks as rLink
from duHast.APISamples import RevitWorksets as rWork
from duHast.APISamples import RevitPurgeUnusedeTransmit as LePurger
from duHast.Utilities.Objects import result as res
from duHast.Utilities import Utility as util

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
    revitFilePath_ = revit_script_util.GetRevitFilePath()
else:
    # get default revit file name in debug mode
    revitFilePath_ = utilM.DEBUG_REVIT_FILE_NAME

# -------------
# my code here:
# -------------

# output messages either to batch processor (debug = False) or console (debug = True)
def Output(message = ''):
    if not debug_:
        revit_script_util.Output(str(message))
    else:
        print (message)

#------------------ workset related

def modify(doc, grid_data):
    '''
    Updates worksets of reference planes, levels, grids, scope boxes

    :param doc: _description_
    :type doc: _type_
    :param grid_data: _description_
    :type grid_data: _type_
    :return: _description_
    :rtype: _type_
    '''

    found_match = False
    return_value = res.Result()
    for file_name, default_workset_name in grid_data:
        if (revit_file_name_.startswith(file_name)):
            found_match = True
            #fix uyp grids
            collector_grids = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid)
            grids_result = rWork.ModifyElementWorkset(doc, default_workset_name, collector_grids, 'grids')
            return_value.Update(grids_result)

            #fix up levels
            collector_levels = rdb.FilteredElementCollector(doc).OfClass(rdb.Level)
            levels_result = rWork.ModifyElementWorkset(doc, default_workset_name, collector_levels, 'levels')
            return_value.Update(levels_result)

            #fix up scope boxes
            collector_scope_boxes = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_VolumeOfInterest)
            scope_boxes_result = rWork.ModifyElementWorkset(doc, default_workset_name, collector_scope_boxes, 'scope boxes')
            return_value.Update(scope_boxes_result)

            #fix up ref planes
            collector_reference_planes = rdb.FilteredElementCollector(doc).OfClass(rdb.ReferencePlane)
            reference_planes_result = rWork.ModifyElementWorkset(doc, default_workset_name, collector_reference_planes,  'reference planes')
            return_value.Update(reference_planes_result)

            break
    if (found_match == False):
        return_value.UpdateSep(False, 'No grid data provided for current Revit file '.format( revit_file_name_))
    return return_value

#------------------ workset related end-----------------------

def modify_views(doc, view_data):
    '''
    Deletes views no longer required.

    :param doc: _description_
    :type doc: _type_
    :param view_data: _description_
    :type view_data: _type_

    :return: _description_
    :rtype: _type_
    '''
    return_value = res.Result()
    match = False
    for file_name, view_rules in view_data:
        if (revit_file_name_.startswith(file_name)):
            collector_views = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
            return_value = rView.DeleteViews(doc, view_rules, collector_views)
            match = True
            break
    if (match == False):
        return_value.UpdateSep(False,'No view filter rule(s) for this file found!')
    return return_value

def modify_sheets(doc, sheets):
    '''
    Deletes sheets no longer required.

    :param doc: _description_
    :type doc: _type_
    :param sheets: _description_
    :type sheets: _type_

    :return: _description_
    :rtype: _type_
    '''

    return_value = res.Result()
    match = False
    for file_name, sheet_rules in sheets:
        if (revit_file_name_.startswith(file_name)):
            collectorSheets = rdb.FilteredElementCollector(doc).OfClass(rdb.View)
            return_value = rView.DeleteSheets(doc, sheet_rules, collectorSheets)
            match = True
            break
    if (match == False):
        return_value.UpdateSep(False,'No sheet filter rule(s) for this file found!')
    return return_value

def build_default_file_list():
    '''
    Reads file data from file and stores it in a global list.

    :return: _description_
    :rtype: _type_
    '''

    rev = com.GetSheetRevByName(doc, utilM.SPLASH_SCREEN_SHEET_NAME)
    flag = True
    match = False
    # read current files
    file_list = utilLocal.read_current_file(utilM.REVISION_DATA_FILEPATH)
    if(file_list is not None and len(file_list) > 0):
        # loop over file data objects and search for match
        print('looking for match:'.format(revit_file_name_))
        for f in file_list:
            print('starts with {}'.format(f.existingFileName))
            if (revit_file_name_.startswith(f.existingFileName) and f.fileExtension == utilM.RVT_FILE_EXTENSION):
                match = True
                f.revision = rev # update with latest revision from sheet
                # pad revision out to three digits if required
                f.revision = util.PadSingleDigitNumericString(f.revision, util.PAD_SINGLE_DIGIT_TO_TWO)
                # store updated file data to be written to marker file
                file_data_.append(f.getData())
                # get new file name for saving as
                new_file_name = f.getNewFileName()
                row_default_new = []
                row_default_new.append(f.existingFileName)
                row_default_new.append(new_file_name)
                default_file_names_.append(row_default_new)
        # check whether we found a match
        flag = match
        # write out marker file
        flag = write_rev_marker_file()
    else:
        flag = False
    return flag

def write_rev_marker_file():
    '''
    Writes out a revision marker file containing the new file revision.

    :return: _description_
    :rtype: _type_
    '''

    status = True
    if(file_data_!= None and len(file_data_) >0):
        # add revit file extension to marker file name
        file_name = root_path_  + \
            '\\' + revit_file_name_ + \
            utilM.RVT_FILE_EXTENSION + \
            utilM.MARKER_FILE_EXTENSION
        status, messageMarker = utilLocal.write_rev_marker_file(file_name, file_data_[0])
        Output(messageMarker)
    else:
        status = False
        Output('Failed to write marker file: No file data found for: {}'.format(revit_file_name_))
    return status

# -------------
# main:
# -------------

# store output here:
root_path_ = utilM.ROOT_PATH

# list containing the default file names:
# populated from text file located in script folder
default_file_names_ = []

# array to contain file information read from text file
file_data_ = []
# the current file name
revit_file_name_ = util.GetFileNameWithoutExt(revitFilePath_)

# model out location including dated folder stamp
root_path_ = root_path_ + '\\' + utilM.MODEL_OUT_FOLDER_NAME

#save revit file to new location
Output('Modifying Revit File.... start')

#flag indicating whether the file can be saved
save_file = build_default_file_list()

if(save_file):
    #check if worksharing needs to be enabled
    if (doc.IsWorkshared == False):
        save_file = com.EnableWorksharing(doc)
        Output('Enabled worksharing.... status: [{}]' .format(save_file.status))

    if save_file:
        result_ = com.SaveAs(doc, root_path_, revitFilePath_, default_file_names_)
        Output('{} :: [{}]'.format(result_.message, result_.status))
    else:
        Output('Not Saving Revit File!!!')

    #make further changes as required....
    flagModifyWorkSets_ = modify(doc, utilM.DEFAULT_WORKSETS)
    Output('{} :: [{}]'.format(flagModifyWorkSets_.message, flagModifyWorkSets_.status))

    # delete views
    resultDeleteViews_ = modify_views(doc, utilM.VIEW_KEEP_RULES)
    Output('{} :: [{}]'.format(resultDeleteViews_.message, resultDeleteViews_.status))
 
    # delete sheets
    resultDeleteSheets_ = modify_sheets(doc, utilM.SHEET_KEEP_RULES)
    Output('{} :: [{}]'.format(resultDeleteSheets_.message,resultDeleteSheets_.status))

    # delete revit links
    if(revit_file_name_.startswith('NHR-BVN-MOD-ARC-NBL-00M-NL00002 - NORTHBLOCK') == False):
        flagDeleteRevitLinks_ = rLink.DeleteRevitLinks(doc)
        Output('{} :: [{}]'.format(flagDeleteRevitLinks_.message,flagDeleteRevitLinks_.status))
    else:
        Output ('Kept Revit Links')

    # purge unused:
    flag_purge_unused_ = LePurger.PurgeUnusedETransmit(doc)
    Output('{} :: [{}]'.format(flag_purge_unused_.message, flag_purge_unused_.status))

    # sync changes back to central
    if (doc.IsWorkshared and debug_ == False):
        Output('Syncing to Central: start')
        syncing_ = com.SyncFile (doc)
        Output('{} :: [{}]'.format(syncing_.message,syncing_.status))
    else:
        Output('Not Saving Revit File!!!')
else:
    Output('Failed to read revision data file. Exiting!!!')

Output('Modifying Revit File.... finished ')