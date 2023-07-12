"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as the second step in exporting models within the  batch processor environment.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- saves a working copy of the revit project file into a temp directory
- deletes all sheets and all 3D views but the views to be exported to .nwc or .ifc from the model to avoid
"generate view x" messages during model export
- models are exported to nwc and ifc format

- export views to nwc based on view filter
- copies exported nwc models into local federated model directory (file names without revision information)
- export views to IFC based on view filter
- optimizes IFC files using solibri ifc optimizer
- copies exported ifc models into local federated model directory (file names without revision information)
- creates separate BIM360 out folder and copies nwc files into ( file names without revision information)

"""

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

# --------------------------
# Imports
# --------------------------
import clr

import os
import settings as settings  # sets up all commonly used variables and path locations!
from utils import utils as utilLocal
from utils.export_nwc import export_views_to_nwc
from utils.export_ifc import export_views_to_ifc, check_name, optimize_ifc_files
from utils.export_file_data import write_out_export_file_data
from duHast.Revit.Views.sheets import get_sheet_rev_by_sheet_name
from duHast.Revit.Views.delete import delete_views_not_on_sheets, delete_all_sheets
from duHast.Revit.Common.file_io import save_as
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.date_stamps import get_folder_date_stamp
from duHast.Utilities.console_out import output

# import common library

from duHast.Utilities.Objects import result as res
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

# the revision of the current Revit model (as per splash screen)
current_file_revision_ = "-"
# store output here, using separate variable since its value is getting changed
models_out_path_ = settings.ROOT_PATH


# this  function needs to be in this module due to the use of global variables!
def build_export_file_name_from_view_ifc(view_name):
    """
    Creates the ifc file name based on the view the file gets exported from.

    - Includes revision information
    - If view starts with predefined Prefix, that prefix will be removed from the name

    :param view_name: The view name.
    :type view_name: str

    :return: The file name based on the view name.
    :rtype: str
    """

    # return newFileName
    if view_name.startswith(settings.EXPORT_IFC_VIEW_PREFIX):
        lenPrefix = len(settings.EXPORT_IFC_VIEW_PREFIX)
        view_name = view_name[lenPrefix:]

        # this is required since the view name does not match the file name required at end of export
        for fd in file_data_:
            if (
                fd.existingFileName == view_name
                and fd.fileExtension == settings.IFC_FILE_EXTENSION
            ):
                # may need to update the revision info!
                if settings.EXPORT_FILES_USE_REVIT_REVISION:
                    # update the revision to the current revit file revision
                    fd.revision = current_file_revision_
                else:
                    # increase rev counter for this file
                    fd.upDateNumericalRev()
                view_name = fd.getNewFileName()
                break

    return view_name + settings.IFC_FILE_EXTENSION


# this  function needs to be in this module due to the use of global variables!
def build_export_file_name_from_view_nwc(view_name):
    """
    Creates the nwc file name based on the view the file gets exported from.

    - Includes revision information
    - If view starts with predefined Prefix, that prefix will be removed from the name

    :param view_name: The view name.
    :type view_name: str

    :return: The file name based on the view name.
    :rtype: str
    """

    len_prefix = len(settings.EXPORT_NWC_VIEW_PREFIX)
    # check if view name starts with NWC_
    if view_name.startswith(settings.EXPORT_NWC_VIEW_PREFIX):
        # remove the prefix from the view name
        view_name = view_name[len_prefix:]

        # this is required since the view name does not match the file name required at end of export
        for fd in file_data_:
            if (
                fd.existingFileName == view_name
                and fd.fileExtension == settings.NWC_FILE_EXTENSION
            ):
                # may need to update the revision info!
                if settings.EXPORT_FILES_USE_REVIT_REVISION:
                    # update the revision to the current revit file revision
                    fd.revision = current_file_revision_
                else:
                    # increase rev counter for this file
                    fd.upDateNumericalRev()
                view_name = fd.getNewFileName()
                break
    return view_name + settings.NWC_FILE_EXTENSION


# -------------
# main:
# -------------

# list containing the default file names:
# [[revit host file name before save, revit host file name after save]]
default_file_names_step_two_ = [
    [
        get_file_name_without_ext(REVIT_FILE_PATH),
        str(get_folder_date_stamp())
        + settings.REVIT_FILE_NAME_PREFIX_EXPORT
        + str(get_file_name_without_ext(REVIT_FILE_PATH)),
    ]
]

# save revit file to new location
output("Modifying Revit File.... start", revit_script_util.Output)

# array to contain file information read from text file
# read default file list info
file_data_ = utilLocal.read_current_file()

# set path to models will be saved to
models_out_path_ = os.path.join(models_out_path_, settings.MODEL_OUT_FOLDER_NAME)
# get the current model revision recorded on sheet splash screen
current_file_revision_ = get_sheet_rev_by_sheet_name(
    doc, settings.SPLASH_SCREEN_SHEET_NAME
)
# the current file name
revit_file_name_ = get_file_name_without_ext(REVIT_FILE_PATH)

# save a working file in temp location
result_ = save_as(
    doc=doc,
    target_directory_path=settings.ROOT_PATH_EXPORT,
    current_full_file_name=REVIT_FILE_PATH,
    name_data=default_file_names_step_two_,
)
output("{} :: [{}]".format(result_.message, result_.status), revit_script_util.Output)

# delete all sheets left in model to avoid any generate view x messages
result_delete_all_sheets_ = delete_all_sheets(doc)
output(
    "{} :: [{}]".format(
        result_delete_all_sheets_.message, result_delete_all_sheets_.status
    ),
    revit_script_util.Output,
)

# delete views not on sheets with exception of views to be exported
result_delete_views_not_on_sheets_ = delete_views_not_on_sheets(doc, check_name)
output(
    "{} :: [{}]".format(
        result_delete_views_not_on_sheets_.message,
        result_delete_views_not_on_sheets_.status,
    ),
    revit_script_util.Output,
)

# start exporting
output("Exporting.... start", revit_script_util.Output)

# export to NWC...
result_export_NWC_ = export_views_to_nwc(
    doc=doc,
    export_view_prefix=settings.EXPORT_NWC_VIEW_PREFIX,
    export_directory=models_out_path_,
    view_name_modifier=build_export_file_name_from_view_nwc,
)
output(
    "{} :: [{}]".format(result_export_NWC_.message, result_export_NWC_.status),
    revit_script_util.Output,
)

# write exported file meta data to file
result_write_meta_nwc_ = write_out_export_file_data(
    export_status=result_export_NWC_,
    message="NWC Export",
    marker_file_extension=settings.MARKER_FILE_EXTENSION,
    file_extension=settings.NWC_FILE_EXTENSION,
    root_path=models_out_path_,
    file_data=file_data_,
    current_file_revision=current_file_revision_,
)
output(
    "{} :: [{}]".format(result_write_meta_nwc_.message, result_write_meta_nwc_.status),
    revit_script_util.Output,
)

# export to IFC file format
result_export_IFC_ = export_views_to_ifc(
    doc=doc,
    export_view_prefix=settings.EXPORT_IFC_VIEW_PREFIX,
    export_directory=models_out_path_,
    view_name_modifier=build_export_file_name_from_view_ifc,
)
output(
    "{} :: [{}]".format(result_export_IFC_.message, result_export_IFC_.status),
    revit_script_util.Output,
)

# write exported file meta data to file
result_write_meta_ifc_ = write_out_export_file_data(
    export_status=result_export_IFC_,
    message="IFC export",
    marker_file_extension=settings.MARKER_FILE_EXTENSION,
    file_extension=settings.IFC_FILE_EXTENSION,
    root_path=models_out_path_,
    file_data=file_data_,
    current_file_revision=current_file_revision_,
)
output(
    "{} :: [{}]".format(result_write_meta_ifc_.message, result_write_meta_ifc_.status),
    revit_script_util.Output,
)

# duplicate NWC's into local federated NWC folder
result_copy_NWCs_ = utilLocal.copy_exports(
    export_status=result_export_NWC_,
    target_folder=settings.ROOT_PATH_NWC,
    file_extension=settings.NWC_FILE_EXTENSION,
    revision_prefix=settings.REVISION_PREFIX,
    revision_suffix=settings.REVISION_SUFFIX,
)
output(
    "{} :: [{}]".format(result_copy_NWCs_.message, result_copy_NWCs_.status),
    revit_script_util.Output,
)

# optimize IFC's prior to copying
result_IFC_optimized_ = optimize_ifc_files(
    export_status=result_export_IFC_, ifc_file_directory=models_out_path_
)
output(
    "{} :: [{}]".format(result_IFC_optimized_.message, result_IFC_optimized_.status),
    revit_script_util.Output,
)

# duplicate IFC's into local federated IFC folder
result_copy_IFCs_ = utilLocal.copy_exports(
    export_status=result_export_IFC_,
    target_folder=settings.ROOT_PATH_IFC,
    file_extension=settings.IFC_FILE_EXTENSION,
    revision_prefix=settings.REVISION_PREFIX,
    revision_suffix=settings.REVISION_SUFFIX,
)
output(
    "{} :: [{}]".format(result_copy_IFCs_.message, result_copy_IFCs_.status),
    revit_script_util.Output,
)

# set up BIM 360 NWC folder (contains nwc files with revision data in name)
setup_BIM360_directory_flag_ = utilLocal.create_bim360_out_folder(
    target_directory=models_out_path_,
    new_subdirectory_name=settings.BIM360_FOLDER_NAME,
)

if setup_BIM360_directory_flag_:
    nwc_export_path = os.path.join(models_out_path_, settings.BIM360_FOLDER_NAME)
    # duplicate NWC's without revision information for bim360 or acc
    result_copy_NWCs_ = utilLocal.copy_exports(
        export_status=result_export_NWC_,
        target_folder=nwc_export_path,
        file_extension=settings.NWC_FILE_EXTENSION,
        revision_prefix=settings.REVISION_PREFIX,
        revision_suffix=settings.REVISION_SUFFIX,
    )
    output(
        "{} :: [{}]".format(result_copy_NWCs_.message, result_copy_NWCs_.status),
        revit_script_util.Output,
    )
else:
    output(
        "failed to set up BIM 360 out folder: {}".format(
            os.path.join(models_out_path_, settings.BIM360_FOLDER_NAME)
        ),
        revit_script_util.Output,
    )

output("Modifying Revit File.... finished ", revit_script_util.Output)
