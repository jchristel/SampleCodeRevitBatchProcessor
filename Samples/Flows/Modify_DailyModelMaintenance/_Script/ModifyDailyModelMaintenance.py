"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module executed as the task script in Revit batch processor.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Updates model health tracer family
- reports model health metrics to text files


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

# reports on:
# - levels, grids, sheets, worksets
# modifies:
# - worksets of levels, grids, scope boxes, reference planes
# - deletes duplicate BVN line patterns
# - deletes 'IMPORT' line patterns
# syncs to central with compact central file option enabled


# debug mode revit project file name
DEBUG_REVIT_FILE_NAME = r"C:\Users\jchristel\Documents\Temp\Debug.rvt"

import clr
import System


# import common library
import settings as settings  # sets up all commonly used variables and path locations!
from utils.mark_views_for_deletion import mark_views_for_deletion
from utils.model_health import update_model_health_tracer_fam, write_model_health_data
from utils import reports as rep
from utils import delete_elements as delElements
from utils.families import reload_families, rename_families
from utils.worksets import (
    modify_element_worksets_with_filters,
    update_workset_default_visibility,
)
from utils.geometry_data import write_out_geometry_data
from utils.warnings_solver import solve_warnings
from utils.check_tag_locations import check_ffe_tags_locations

from duHast.Utilities.console_out import output
from duHast.Utilities.Objects.timer import Timer
from duHast.Revit.Common.file_io import sync_file
from duHast.Revit.BIM360.bim_360 import get_bim_360_path, convert_bim_360_file_path


clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)
clr.AddReference("System")


# flag whether this runs in debug or not
debug_ = False

# Add batch processor scripting references
if not debug_:
    import revit_script_util
    import revit_file_util

    clr.AddReference("RevitAPI")
    clr.AddReference("RevitAPIUI")
    # NOTE: these only make sense for batch Revit file processing mode.
    doc = revit_script_util.GetScriptDocument()
    revitFilePath_ = revit_script_util.GetRevitFilePath()
else:
    # get default revit file name
    revitFilePath_ = DEBUG_REVIT_FILE_NAME


# update to cope with cloud based file path
if(settings.IS_CLOUD_PROJECT):
    cloudPath = get_bim_360_path(doc)
    revitFilePath_ = convert_bim_360_file_path(cloudPath)

# -------------
# my code here:
# -------------


# -------------
# main:
# -------------

# actions to execute expecting doc only as argument
ACTIONS = [
    update_model_health_tracer_fam,
    write_model_health_data,
    delElements.delete_line_pattern_starting_with_import,
    delElements.delete_sample_duplicate_patterns,
    delElements.delete_unused_elev_view_markers,
    delElements.delete_unwanted_shared_parameters,
    delElements.delete_duplicate_line_pattern_names,
    write_out_geometry_data,
    rep.report_sheets,
    rep.report_sheets_short,
    rep.report_shared_paras,
    rep.report_levels,
    rep.report_grids,
    rep.report_families,
    rep.report_worksets,
    rep.report_views_filtered,
    rep.report_wall_types,
    rep.report_cad_link_data,
    rep.report_revit_link_data,
    modify_element_worksets_with_filters,
    update_workset_default_visibility,
    solve_warnings,
    rename_families,
    rep.report_ffe_tags, # needs to run before families are reloaded to be able to restore tag location after reload
    reload_families,
    check_ffe_tags_locations, # needs to run after families are reloaded to restore tag location after reload
    mark_views_for_deletion,
]

# save revit file to new location
output("Modifying Revit File.... start", revit_script_util.Output)


def output_modules(message):
    """
    Output function for the modules called. Pipes message to batch processor

    :param message: The message
    :type message: str
    """

    output(message, revit_script_util.Output)


# execute all actions
t = Timer()
for action in ACTIONS:
    try:
        t.start()
        flag = action(doc, revitFilePath_, output_modules)
        output(flag.message, revit_script_util.Output)  # TODO: add spacer characters?
        output("status: [{}]".format(flag.status, t.stop()), revit_script_util.Output)
        output("-", revit_script_util.Output)
    except Exception as e:
        output(
            "Failed to execute action: {} with exception {}".format(action, e),
            revit_script_util.Output,
        )
    finally:
        if t.is_running():
            t.stop()

# sync changes back to central
if debug_ == False:
    # ------------------------------------- syncing -------------------------------------

    # finally sync model and get rid of old file data (compress model)
    output(
        "Syncing to Central with compact central file option enabled: start",
        revit_script_util.Output,
    )
    syncing_ = sync_file(doc, True)
    output(
        "Syncing to Central: finished [{}]".format(syncing_.status),
        revit_script_util.Output,
    )

output("Modifying Revit File.... finished ", revit_script_util.Output)
