#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
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

from duHast.Revit.Links.links import delete_revit_links
from duHast.Revit.Purge.purge_unused_e_transmit import purge_unused_e_transmit

from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.console_out import output
from duHast.Utilities.Objects import result as res

from utils.worksets import modify
from utils.views import modify_sheets, modify_views
from utils.revision_marker_files import write_rev_marker_file
from utils.utils import build_default_file_list


# required in lambda expressions!
clr.AddReference("System.Core")
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
root_path_ = root_path_ + "\\" + settings.MODEL_OUT_FOLDER_NAME

# save revit file to new location
output("Modifying Revit File.... start", revit_script_util.Output)

# flag indicating whether the file can be saved
save_file, default_file_names_, marker_file_data_ = build_default_file_list(
    doc, 
    settings.REVISION_DATA_FILEPATH, 
    revit_file_name_, 
    settings.SPLASH_SCREEN_SHEET_NAME, 
    settings.RVT_FILE_EXTENSION
)

if save_file.status:
    # store retrieved marker file data
    file_data_.append(marker_file_data_)

    # write out marker file
    flag_status = write_rev_marker_file(
        file_data_,
        root_path_,
        revit_file_name_,
        settings.RVT_FILE_EXTENSION,
        settings.MARKER_FILE_EXTENSION
    )
    output(flag_status.message, revit_script_util.Output)

    # check if worksharing needs to be enabled
    if doc.IsWorkshared == False:
        save_file = enable_worksharing(doc)
        output(
            "Enabled worksharing.... status: [{}]".format(save_file.status),
            revit_script_util.Output,
        )

    if save_file:
        result_ = save_as(doc, root_path_, REVIT_FILE_PATH, default_file_names_)
        output(
            "{} :: [{}]".format(result_.message, result_.status),
            revit_script_util.Output,
        )
    else:
        output("Not Saving Revit File!!!", revit_script_util.Output)

    # make further changes as required....
    flagModifyWorkSets_ = modify(
        doc=doc, grid_data=settings.DEFAULT_WORKSETS, revit_file_name=revit_file_name_
    )
    output(
        "{} :: [{}]".format(flagModifyWorkSets_.message, flagModifyWorkSets_.status),
        revit_script_util.Output,
    )

    # delete views
    resultDeleteViews_ = modify_views(
        doc=doc, view_data=settings.VIEW_KEEP_RULES, revit_file_name=revit_file_name_
    )
    output(
        "{} :: [{}]".format(resultDeleteViews_.message, resultDeleteViews_.status),
        revit_script_util.Output,
    )

    # delete sheets
    resultDeleteSheets_ = modify_sheets(
        doc=doc, sheets=settings.SHEET_KEEP_RULES, revit_file_name=revit_file_name_
    )
    output(
        "{} :: [{}]".format(resultDeleteSheets_.message, resultDeleteSheets_.status),
        revit_script_util.Output,
    )

    # delete revit links
    if (
        revit_file_name_ not in utilLocal.DO_NOT_DELETE_LINKS
    ):
        flagDeleteRevitLinks_ = delete_revit_links(doc)
        output(
            "{} :: [{}]".format(
                flagDeleteRevitLinks_.message, flagDeleteRevitLinks_.status
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
    if doc.IsWorkshared == False:
        output("Syncing to Central: start", revit_script_util.Output)
        syncing_ = sync_file(doc)
        output(
            "{} :: [{}]".format(syncing_.message, syncing_.status),
            revit_script_util.Output,
        )
    else:
        output("Not Saving Revit File!!!", revit_script_util.Output)
else:
    output("Failed to read revision data file. Exiting!!!", revit_script_util.Output)

output("Modifying Revit File.... finished ", revit_script_util.Output)
