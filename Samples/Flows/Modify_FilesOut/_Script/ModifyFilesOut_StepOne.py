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

import settings as settings  # sets up all commonly used variables and path locations!
from utils import utils as utilLocal

from duHast.Revit.Common.file_io import enable_worksharing, save_as, sync_file
from duHast.Revit.Common.worksets import modify_element_workset
from duHast.Revit.Links.links import delete_revit_links
from duHast.Revit.Purge.purge_unused_e_transmit import purge_unused_e_transmit
from duHast.Revit.Views.delete import delete_views, delete_sheets
from duHast.Revit.Views.sheets import get_all_sheets, get_sheet_rev_by_sheet_name
from duHast.Revit.Views.views import get_views_in_model
from duHast.Utilities.utility import pad_single_digit_numeric_string
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.console_out import output
from duHast.Utilities.Objects import result as res


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
    revitFilePath_ = settings.DEBUG_REVIT_FILE_NAME

# -------------
# my code here:
# -------------

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
            grids_result = modify_element_workset(doc, default_workset_name, collector_grids, 'grids')
            return_value.Update(grids_result)

            #fix up levels
            collector_levels = rdb.FilteredElementCollector(doc).OfClass(rdb.Level)
            levels_result = modify_element_workset(doc, default_workset_name, collector_levels, 'levels')
            return_value.Update(levels_result)

            #fix up scope boxes
            collector_scope_boxes = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_VolumeOfInterest)
            scope_boxes_result = modify_element_workset(doc, default_workset_name, collector_scope_boxes, 'scope boxes')
            return_value.Update(scope_boxes_result)

            #fix up ref planes
            collector_reference_planes = rdb.FilteredElementCollector(doc).OfClass(rdb.ReferencePlane)
            reference_planes_result = modify_element_workset(doc, default_workset_name, collector_reference_planes,  'reference planes')
            return_value.Update(reference_planes_result)

            break
    if (found_match == False):
        return_value.update_sep(False, 'No grid data provided for current Revit file '.format( revit_file_name_))
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

            # default view filter (returning true for any view past in)
            def view_filter(view):
                return True
            # get views in model
            collector_views = get_views_in_model(doc, view_filter)
            rdb.FilteredElementCollector(doc).OfClass(rdb.View)
            return_value = delete_views(doc, view_rules, collector_views)
            match = True
            break
    if (match == False):
        return_value.update_sep(False,'No view filter rule(s) for this file found!')
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
            collectorSheets = get_all_sheets(doc)
            return_value = delete_sheets(doc, sheet_rules, collectorSheets)
            match = True
            break
    if (match == False):
        return_value.update_sep(False,'No sheet filter rule(s) for this file found!')
    return return_value

def build_default_file_list():
    '''
    Reads file data from file and stores it in a global list.

    :return: _description_
    :rtype: _type_
    '''

    rev = get_sheet_rev_by_sheet_name(doc, settings.SPLASH_SCREEN_SHEET_NAME)
    flag = True
    match = False
    # read current files
    file_list = utilLocal.read_current_file(settings.REVISION_DATA_FILEPATH)
    if(file_list is not None and len(file_list) > 0):
        # loop over file data objects and search for match
        output('looking for match:'.format(revit_file_name_), revit_script_util.Output)
        for f in file_list:
            output('starts with {}'.format(f.existing_file_name), revit_script_util.Output)
            if (revit_file_name_.startswith(f.existing_file_name) and f.file_extension == settings.RVT_FILE_EXTENSION):
                match = True
                f.revision = rev # update with latest revision from sheet
                # pad revision out to two digits if required
                f.revision = pad_single_digit_numeric_string(f.revision)
                # store updated file data to be written to marker file
                file_data_.append(f.get_data())
                # get new file name for saving as
                new_file_name = f.get_new_file_name()
                row_default_new = []
                row_default_new.append(f.existing_file_name)
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
            settings.RVT_FILE_EXTENSION + \
            settings.MARKER_FILE_EXTENSION
        status, messageMarker = utilLocal.write_rev_marker_file(file_name, file_data_[0])
        output(messageMarker, revit_script_util.Output)
    else:
        status = False
        output('Failed to write marker file: No file data found for: {}'.format(revit_file_name_), revit_script_util.Output)
    return status

# -------------
# main:
# -------------

# store output here:
root_path_ = settings.ROOT_PATH

# list containing the default file names:
# populated from text file located in script folder
default_file_names_ = []

# array to contain file information read from text file
file_data_ = []
# the current file name
revit_file_name_ = get_file_name_without_ext(revitFilePath_)

# model out location including dated folder stamp
root_path_ = root_path_ + '\\' + settings.MODEL_OUT_FOLDER_NAME

#save revit file to new location
output('Modifying Revit File.... start', revit_script_util.Output)

#flag indicating whether the file can be saved
save_file = build_default_file_list()

if(save_file):
    #check if worksharing needs to be enabled
    if (doc.IsWorkshared == False):
        save_file = enable_worksharing(doc)
        output('Enabled worksharing.... status: [{}]' .format(save_file.status), revit_script_util.Output)

    if save_file:
        result_ = save_as(doc, root_path_, revitFilePath_, default_file_names_)
        output('{} :: [{}]'.format(result_.message, result_.status), revit_script_util.Output)
    else:
        output('Not Saving Revit File!!!', revit_script_util.Output)

    #make further changes as required....
    flagModifyWorkSets_ = modify(doc, settings.DEFAULT_WORKSETS)
    output('{} :: [{}]'.format(flagModifyWorkSets_.message, flagModifyWorkSets_.status), revit_script_util.Output)

    # delete views
    resultDeleteViews_ = modify_views(doc, settings.VIEW_KEEP_RULES)
    output('{} :: [{}]'.format(resultDeleteViews_.message, resultDeleteViews_.status), revit_script_util.Output)
 
    # delete sheets
    resultDeleteSheets_ = modify_sheets(doc, settings.SHEET_KEEP_RULES)
    output('{} :: [{}]'.format(resultDeleteSheets_.message,resultDeleteSheets_.status), revit_script_util.Output)

    # delete revit links
    if(revit_file_name_.startswith('Sample file name') == False):
        flagDeleteRevitLinks_ = delete_revit_links(doc)
        output('{} :: [{}]'.format(flagDeleteRevitLinks_.message,flagDeleteRevitLinks_.status), revit_script_util.Output)
    else:
        output ('Kept Revit Links', revit_script_util.Output)

    # purge unused:
    flag_purge_unused_ = purge_unused_e_transmit(doc)
    output('{} :: [{}]'.format(flag_purge_unused_.message, flag_purge_unused_.status), revit_script_util.Output)

    # sync changes back to central
    if (doc.IsWorkshared and debug_ == False):
        output('Syncing to Central: start', revit_script_util.Output)
        syncing_ = sync_file (doc)
        output('{} :: [{}]'.format(syncing_.message,syncing_.status), revit_script_util.Output)
    else:
        output('Not Saving Revit File!!!', revit_script_util.Output)
else:
    output('Failed to read revision data file. Exiting!!!', revit_script_util.Output)

output('Modifying Revit File.... finished ', revit_script_util.Output)