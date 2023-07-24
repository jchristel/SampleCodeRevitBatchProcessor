"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as the first step in exporting models within the  batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- saves a working copy of the revit project file into the designated export directory

    - file has revision information added to the file name
    - file will be saved as a workshared file ( even if not set up as a workshared file)

- the following elements are placed on a designated workset:

    - levels
    - grids
    - scope boxes
    - reference planes

- deletes sheets and views depending on properties filter defined in settings file

    - some projects require a set of sheets and views to be retained in the shared model

- removes all revit links:
    
    - in step 1 files are opened with all worksets closed to speed up the process (links are therefore not opened)
    - in step 2 files are opened with all worksets opened ( revit links are deleted at that point)

- purge unused elements

    - requires eTransmit to be installed (!)

"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

# --------------------------
# Imports
# --------------------------

import clr
import os

import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Revit.Common.file_io import enable_worksharing, save_as, sync_file

from duHast.Revit.Links.links import delete_revit_links
from duHast.Revit.Purge.purge_unused_e_transmit import purge_unused_e_transmit

from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.console_out import output
from duHast.Utilities.Objects import result as res

from utils.worksets import modify
from utils.views import modify_sheets, modify_views
from utils.revision_marker_files import write_rev_marker_file
from utils.docFile_utils import build_default_file_list


# required in lambda expressions!
clr.AddReference("System.Core")
import System
clr.ImportExtensions(System.Linq)

import Autodesk.Revit.DB as rdb

import revit_script_util
import revit_file_util

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

# NOTE: these only make sense for batch Revit file processing mode.
doc = revit_script_util.GetScriptDocument()
REVIT_FILE_PATH = revit_script_util.GetRevitFilePath()

# -------------
# my code here:
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
revit_file_name_ = get_file_name_without_ext(REVIT_FILE_PATH)

# model out location including dated folder stamp
root_path_ = os.path.join(root_path_, settings.MODEL_OUT_FOLDER_NAME)

def out(message):
    output(message, revit_script_util.Output)

output("Modifying Revit File.... start", revit_script_util.Output)

# flag indicating whether the file can be saved
save_file, default_file_names_, marker_file_data_ = build_default_file_list(
    doc=doc,
    revision_data_file_path=settings.REVISION_DATA_FILEPATH,
    revit_file_name=revit_file_name_,
    splash_screen_name=settings.SPLASH_SCREEN_SHEET_NAME,
    revit_file_extension=settings.RVT_FILE_EXTENSION
)

if save_file.status:
    # store retrieved marker file data
    file_data_ = marker_file_data_
    # write out marker file
    flag_status = write_rev_marker_file(
        file_data=file_data_,
        root_path=root_path_,
        revit_file_name=revit_file_name_,
        revit_file_extension=settings.RVT_FILE_EXTENSION,
        marker_file_extension=settings.MARKER_FILE_EXTENSION
    )
    output(flag_status.message, revit_script_util.Output)

    # check if worksharing needs to be enabled
    if doc.IsWorkshared == False:
        save_file = enable_worksharing(doc)
        output(
            "Enabled worksharing.... status: [{}]".format(save_file.status),
            revit_script_util.Output,
        )

    # save revit file to new location
    if save_file.status:
        result_ = save_as(
            doc=doc,
            target_directory_path=root_path_,
            current_full_file_name=REVIT_FILE_PATH,
            name_data=default_file_names_,
        )
        output(
            "{} :: [{}]".format(result_.message, result_.status),
            revit_script_util.Output,
        )
    else:
        output("Not Saving Revit File!!!", revit_script_util.Output)

    # make further changes as required....
    # move elements to worksets
    result_modify_worksets_ = modify(
        doc=doc, grid_data=settings.DEFAULT_WORKSETS, revit_file_name=revit_file_name_
    )
    output(
        "{} :: [{}]".format(
            result_modify_worksets_.message, result_modify_worksets_.status
        ),
        revit_script_util.Output,
    )

    # delete views as per filter
    result_delete_views_ = modify_views(
        doc=doc, view_data=settings.VIEW_KEEP_RULES, revit_file_name=revit_file_name_
    )
    output(
        "{} :: [{}]".format(result_delete_views_.message, result_delete_views_.status),
        revit_script_util.Output,
    )

    # delete sheets as per filter
    result_delete_sheets_ = modify_sheets(
        doc=doc, sheets=settings.SHEET_KEEP_RULES, revit_file_name=revit_file_name_
    )
    output(
        "{} :: [{}]".format(
            result_delete_sheets_.message, result_delete_sheets_.status
        ),
        revit_script_util.Output,
    )

    # delete revit links
    if revit_file_name_ not in settings.DO_NOT_DELETE_LINKS:
        result_delete_revit_links_ = delete_revit_links(doc)
        output(
            "{} :: [{}]".format(
                result_delete_revit_links_.message, result_delete_revit_links_.status
            ),
            revit_script_util.Output,
        )
    else:
        output("Kept Revit Links", revit_script_util.Output)

    # purge unused:
    flag_purge_unused_ = purge_unused_e_transmit(doc)
    output(
        "{} :: [{}]".format(flag_purge_unused_.message, flag_purge_unused_.status),
        revit_script_util.Output,
    )

    # sync changes back to central
    if doc.IsWorkshared:
        output("Syncing to Central: start", revit_script_util.Output)
        syncing_ = sync_file(doc)
        output(
            "{} :: [{}]".format(syncing_.message, syncing_.status),
            revit_script_util.Output,
        )
    else:
        output(
            "Revit file is not a workshared document. Not saving Revit file!",
            revit_script_util.Output,
        )
else:
    output("Failed to read revision data file. Exiting!!!", revit_script_util.Output)

output("Modifying Revit File.... finished ", revit_script_util.Output)
