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

# this sample re-creates a central file by detaching the original file and then creating a new central file with the same name
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
import os

import settings as settings  # sets up all commonly used variables and path locations!

# import common library
from duHast.Utilities.console_out import output
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Revit.Common.file_io import save_as_family
from duHast.Revit.Family.family_reload import reload_all_families
from duHast.Utilities.Objects.timer import Timer


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

# -------------
# main:
# -------------

# setup timer
t = Timer()
t.start()

# debug test
output(
    "Script directory: {}".format(settings.SCRIPT_DIRECTORY),
    revit_script_util.Output,
)

output(
    "Modifying Revit File.... start",
    revit_script_util.Output,
)

# start reload
_flag_reload = reload_all_families(
    doc, settings.REVIT_LIBRARY_PATH, settings.REVIT_LIBRARY_INCLUDE_SUB_DIRS_IN_SEARCH
)

# show results
output(
    _flag_reload.message,
    revit_script_util.Output,
)
output(
    "Overall reload status: [{}]".format(_flag_reload.status),
    revit_script_util.Output,
)
output(
    "{}".format(t.stop()),
    revit_script_util.Output,
)

# get the file name
_file_name_without_ext = get_file_name_without_ext(REVIT_FILE_PATH)
REVIT_FILE_PATH_NEW = os.path.join(
    settings.WORKING_DIRECTORY, _file_name_without_ext + ".rfa"
)

# save file if required
if True:
    # save family file
    output(
        "Saving family file: start",
        revit_script_util.Output,
    )
    syncing_ = save_as_family(
        doc,
        settings.WORKING_DIRECTORY,
        REVIT_FILE_PATH,
        [[_file_name_without_ext, _file_name_without_ext]],
        settings.FILE_EXTENSION_OF_FILES_TO_PROCESS,
        True,
    )

    output(
        "Saving family file: finished {} :: [{}]".format(
            syncing_.message, syncing_.status
        ),
        revit_script_util.Output,
    )
    # save marker file
    # save marker file
    if syncing_.status == False:
        output(
            str(syncing_.message),
            revit_script_util.Output,
        )
    else:
        # write marker file
        _file_name_marker = os.path.join(
            settings.WORKING_DIRECTORY, _file_name_without_ext + "_marker_.temp"
        )
        try:
            write_report_data_as_csv(
                _file_name_marker,
                "",
                [["Copy From", "Copy To"], [REVIT_FILE_PATH_NEW, REVIT_FILE_PATH]],
            )
            output("Wrote marker file: {} :: {}".format(_file_name_marker, True))
        except Exception as e:
            output(
                "Wrote marker file: {} :: {} with exception: {}".format(
                    _file_name_marker, False, e
                )
            )
