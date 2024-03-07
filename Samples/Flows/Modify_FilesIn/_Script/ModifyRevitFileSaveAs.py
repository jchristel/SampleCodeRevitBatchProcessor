"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains the main script executed by batch processor for each consultant Revit file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Actions:

- enable worksharing
- purge unused
- clean up grids, levels, scope boxes, reference planes worksets
- save as ( new file name based on file data stored in csv file)
- options( delete cad and Revit links)

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

# --------------------------
# default file path locations
# --------------------------


import clr, sys
import System

# set path to common library
import settings as settings  # sets up all commonly used variables and path locations!

from duHast.Revit.Common.file_io import enable_worksharing, save_as, sync_file

from duHast.Revit.Links.links import delete_revit_links
from duHast.Revit.Links.cad_links import delete_cad_links
from duHast.Revit.Purge.purge_unused_e_transmit import purge_unused_e_transmit

from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.console_out import output
from duHast.Revit.BIM360.bim_360 import get_bim_360_path, convert_bim_360_file_path

from utils.worksets import modify
from utils.file_data import get_file_data_by_name, get_file_data


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

# list containing the default file names:
# [[revit host file name before save, revit host file name after save]]
_default_file_names = []
# list of filedata elements
_default_file_data = []

# flag indicating whether the file can be saved
_save_file = True

# workset mapping data in format:
# [["Revit project file name start", "workset name"]]
_default_worksets = []


# builds the default file names list
def build_default_file_names(revit_file_path):
    """
    Build the default file names list for the current file from the file data list.

    :param revit_file_path: revit file path
    :type revit_file_path: str
    """

    revit_file_name = get_file_name_without_ext(revit_file_path)
    file_data = get_file_data_by_name(_current_document_data, revit_file_name)
    if file_data != None:
        _default_file_data.append(file_data)
        dummy = [file_data.existing_file_name, file_data.new_file_name]
        _default_file_names.append(dummy)
    else:
        output("Found no match for: {}".format(revit_file_name), revit_script_util.Output)


# -------------
# main:
# -------------

# store output here
_root_path = settings.ROOT_PATH_REVIT_DEFAULT
# read all file settings
_current_document_data_result = get_file_data()
if(_current_document_data_result.status == False):
    output(
        "Error reading file data: {}".format(_current_document_data_result.message),
        revit_script_util.Output,
    )
    sys.exit(1)

_current_document_data = _current_document_data_result.result
output(
    "Read file data: {} item(s) read.".format(len(_current_document_data)),
    revit_script_util.Output,
)

# populate default file names list with entry matching this file
build_default_file_names(REVIT_FILE_PATH)

# save revit file to new location
output("Modifying Revit File.... start", revit_script_util.Output)

# get the folder path where to save the file, and workset naming
for f in _default_file_data:
    if (
        _revit_file_name.startswith(f.existing_file_name)
        and f.file_extension == settings.FILE_EXTENSION_OF_FILES_TO_PROCESS
    ):
        # get save as location
        _root_path = f.save_as_location
        # get workset mapping
        _default_worksets.append( f.levels_and_grids_workset)
        output(
            "Setting target folder to:  {}".format(_root_path, revit_script_util.Output)
        )
        break

# check if worksharing needs to be enabled
if doc.IsWorkshared == False:
    # save revit file to new location
    output("Enabling worksharing.... start", revit_script_util.Output)
    _enable_worksharing_status = enable_worksharing(doc)
    # store for further processing down the line
    _save_file = _enable_worksharing_status.status
    if(_enable_worksharing_status.status == False):
        output(
            "Failed to enable worksharing.... status: [{}]".format(
                _enable_worksharing_status.message
            ),
            revit_script_util.Output,
        )
    else:
        output(
            "Enabled worksharing.... status: [{}]".format(_enable_worksharing_status.status),
            revit_script_util.Output,
        )

if _save_file:
    result_ = save_as(
        doc=doc,
        target_directory_path=_root_path,
        current_full_file_name=REVIT_FILE_PATH,
        name_data=_default_file_names,
    )
    output(
        "{} :: [{}]".format(result_.message, result_.status),
        revit_script_util.Output,
    )
else:
    output("Not Saving Revit File!!!", revit_script_util.Output)

# make further changes as required....

if(len(_default_worksets) == 0):
    output("No workset data provided for current Revit file {}".format(_revit_file_name), revit_script_util.Output)
else:
    # modify worksets
    _modify_workSets_result = modify(doc, _default_worksets[0])
    output(
        "{} :: [{}]".format(
            _modify_workSets_result.message, _modify_workSets_result.status
        ),
        revit_script_util.Output,
    )

# purge unused:
_purge_unused_result = purge_unused_e_transmit(doc)
output(
    "{} :: [{}]".format(_purge_unused_result.message, _purge_unused_result.status),
    revit_script_util.Output,
)

# check if any links are to be deleted
if(settings.DELETE_LINKS):
    # delete revit links
    _delete_links_result = delete_revit_links(doc)
    output(
        "{} :: [{}]".format(_delete_links_result.message, _delete_links_result.status),
        revit_script_util.Output,
    )
    # delete cad links
    _delete_cad_links_result = delete_cad_links(doc)
    output(
        "{} :: [{}]".format(_delete_cad_links_result.message, _delete_cad_links_result.status),
        revit_script_util.Output,
    )
else:
    output("Not deleting any links!", revit_script_util.Output)

# sync changes back to central
if doc.IsWorkshared:
    output("Syncing to Central: start", revit_script_util.Output)
    _syncing = sync_file(doc)
    output(
        "{} :: [{}]".format(_syncing.message, _syncing.status),
        revit_script_util.Output,
    )
else:
    output(
        "Revit file is not a workshared document. Not saving Revit file!",
        revit_script_util.Output,
    )

output("Modifying Revit File.... finished ", revit_script_util.Output)
