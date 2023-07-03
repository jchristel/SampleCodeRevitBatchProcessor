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
# Copyright (c) 2023  Jan Christel
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

# reports on:
# - levels, grids, sheets, worksets
# modifies:
# - worksets of levels, grids, scope boxes, reference planes
# - deletes duplicate BVN line patterns
# - deletes 'IMPORT' line patterns
# syncs to central with compact central file option enabled


# TODO:
# - check all reports have a header row since combine files expects files with a header row
# - reports as CSV files
# - check any combine action works with csv file output
# - all action functions need to accept the file path in addition to the document


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
from duHast.Utilities.timer import Timer
from duHast.Revit.Common.file_io import sync_file


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
    delElements.delete_bvn_duplicate_patterns,
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
    t.start()
    flag = action(doc, revitFilePath_, output_modules)
    output(flag.message, revit_script_util.Output)  # TODO: add spacer characters?
    output("status: [{}]".format(flag.status, t.stop()), revit_script_util.Output)
    output("-", revit_script_util.Output)

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
