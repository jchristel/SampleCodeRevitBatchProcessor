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

import settings as settings # sets up all commonly used variables and path locations!
from utils import utils as utilLocal
from duHast.Utilities.Objects import result as res
from duHast.Utilities import Utility as util

# -------------
# my code here:
# -------------

# output messages
def Output(message = ''):
    print (message)


def get_revit_file_names(revit_file_directory):
    '''
    Get Revit file data from output folder.
    
    :return: 
        Result class instance.

        - False if no Revit files where found, otherwise True.
        - result.message will contain 'Got Revit files.'.
        - result.result will contain list of lists in format [[directory path, file name]]

        On exception:

        - result.status (bool) will be False.
        - result.message will contain the exception message.
        - result.result will be an empty list.

    :rtype: :class:`.Result`
    '''

    return_value = res.Result()

    # get revit files in folder
    revit_files = util.GetFilesWithFilter(
        revit_file_directory
       )

    copy_data = []
    if(len(revit_files) > 0):
        for revit_file in revit_files:
            directory_path = util.GetFolderPathFromFile(revit_file)
            row = [
                directory_path,
                revit_file[len(directory_path) + 1 :]
            ]
            copy_data.append(row)
        return_value.UpdateSep(True, 'Got Revit files.')
        return_value.result = copy_data
    else:
        return_value.UpdateSep(False, 'Failed to get any Revit files.')
    return return_value

# -------------
# main:
# -------------

# store output here:
root_path_ = settings.ROOT_PATH
# build out directory location
root_path_ = root_path_ + '\\' + settings.MODEL_OUT_FOLDER_NAME

# set up BIM 360 NWC folder
set_up_bim360_folder_flag_ = utilLocal.create_bim360_out_folder(root_path_)
# if wqe have a BIM 360 folder copy revit files into it
if(set_up_bim360_folder_flag_):
    # set up a result class object with data from marker files
    export_revit_status = get_revit_file_names(root_path_)
    # build the full folder path to where files are to be copied to
    revit_export_path = root_path_+ '\\' + settings.BIM360_FOLDER_NAME
    # duplicate revit files (but strip their revision information)
    flag_copy_revit_ = utilLocal.copy_exports(
        export_revit_status, 
        root_path_ + '\\' + settings.BIM360_FOLDER_NAME, 
        settings.RVT_FILE_EXTENSION
    )
    Output('{} :: [{}]'.format(flag_copy_revit_.message, flag_copy_revit_.status))
else:
    Output('failed to set up BIM 360 out folder')
