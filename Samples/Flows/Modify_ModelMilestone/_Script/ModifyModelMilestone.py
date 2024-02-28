#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

# this sample re-creates a central file by detaching the original file and then creating a new central file with a modified name in a back up location
# in the same location
# batch processor settings should be
# - all worksets closed
# - audit on opening
# - preserve worskets
# the SaveAs() method will compress the newly created central file by default

# --------------------------
# default file path locations
# --------------------------

import clr
import System
import os

# set path to common library
import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Revit.Common.file_io import save_as, sync_file
from duHast.Revit.BIM360.bim_360 import get_bim_360_path, convert_bim_360_file_path

from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.console_out import output
from duHast.Utilities.date_stamps import get_folder_date_stamp, FOLDER_DATE_STAMP_YYMMDD
from duHast.Utilities.directory_io import create_target_directory

clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)


import revit_script_util
import revit_file_util

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

# NOTE: these only make sense for batch Revit file processing mode.
doc = revit_script_util.GetScriptDocument()
REVIT_FILE_PATH = revit_script_util.GetRevitFilePath()

# update to cope with cloud based file path
if settings.IS_CLOUD_PROJECT:
    cloudPath = get_bim_360_path(doc)
    REVIT_FILE_PATH = convert_bim_360_file_path(cloudPath)

# -------------
# my code here:
# -------------

# the current file name
_revit_file_name = get_file_name_without_ext(REVIT_FILE_PATH)

# -------------
# main:
# -------------

# list containing the default file names:
# [[revit host file name before save, revit host file name after save]]
defaultFileNames_ = [
    [
        _revit_file_name,
        "{}{}{}".format(
            get_folder_date_stamp(FOLDER_DATE_STAMP_YYMMDD),
            settings.MILESTONE_FILE_PREFIX,
            _revit_file_name,
        ),
    ]
]

# save revit file to new location
output("Modifying Revit File.... start", revit_script_util.Output)

# build the milestone directory name
_milestone_directory_name = get_folder_date_stamp() + settings.MILESTONE_DIRECTORY_NAME

# create  milestone directory
_flag_got_milestone_directory = create_target_directory(
    settings.ROOT_PATH_REVIT, _milestone_directory_name
)
output(
    "Milestone directory: {}".format(_milestone_directory_name),
    revit_script_util.Output,
)


if _flag_got_milestone_directory:
    result_ = save_as(
        doc,
        os.path.join(settings.ROOT_PATH_REVIT, _milestone_directory_name),
        REVIT_FILE_PATH,
        defaultFileNames_,
    )
    output(
        "{} :: [{}]".format(result_.message, result_.status), revit_script_util.Output
    )
    # sync changes back to central

    output("Syncing to Central: start", revit_script_util.Output)
    syncing_ = sync_file(doc)
    output(
        "Syncing to Central: finished [{}]".format(syncing_.status),
        revit_script_util.Output,
    )
else:
    output(
        "failed to create target folder {} ".format(
            os.path.join(settings.ROOT_PATH_REVIT, _milestone_directory_name)
        ),
        revit_script_util.Output,
    )

output("Modifying Revit File.... finished ", revit_script_util.Output)
