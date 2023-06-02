"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module running Revit related tests as the main script within batch processor flow. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

# this sample moves revit link instances onto a workset specified in list

# --------------------------
# Imports
# --------------------------
import os.path
import utilRevitTests as utilM  # sets up all commonly used variables and path locations!

# get document and import revit batch processor
from test.utils.rbp_setup import add_rbp_ref
from duHast.Utilities.console_out import output, output_header
from duHast.Utilities.files_csv import write_report_data_as_csv
from duHast.Utilities.files_io import get_file_name_without_ext
import revit_script_util

# get the document from revit batch processor
doc = add_rbp_ref()

# flag whether this runs in debug or not
DEBUG = False

# -------------
# my code here:
# -------------

#: import test runners
from test.Revit.Common.run_test_classes import (
    run_design_set_options_tests as run_des_tests,
)
from test.Revit.Revision.run_test_classes import run_revision_tests as run_rev_tests
from test.Revit.Views.run_test_classes import run_views_tests as run_view_tests
from test.Revit.Walls.run_test_classes import run_walls_tests as run_wall_tests
from test.Revit.Levels.run_test_classes import run_levels_tests as run_levels_tests
from test.Revit.Grids.run_test_classes import run_grids_tests as run_grids_tests
from test.Revit.SharedParameters.run_test_classes import run_shared_parameters_tests

#: add test runners to list
TESTS = [
    run_des_tests,
    run_rev_tests,
    run_view_tests,
    run_wall_tests,
    run_grids_tests,
    run_levels_tests,
    run_shared_parameters_tests,
]

#: execute tests
output_header("Executing tests.... start", revit_script_util.Output)
#: test log file
file_name = os.path.join(
    utilM.OUTPUT_FOLDER, get_file_name_without_ext(doc.Title) + ".csv"
)
#: overwrite previous test date at log file open
write_mode = "w"

counter = 0
for test in TESTS:
    output_header('starting test group: {}'.format(counter), revit_script_util.Output)
    try:
        result = test(doc)
        for test_result in result.result:
            # write results to file
            write_report_data_as_csv(
                file_name,
                "",
                [[test_result[3], test_result[4], test_result[5]]],
                write_mode,
            )
            # provide short summary only...more details in log file
            output(test_result[0], revit_script_util.Output)
            output(test_result[2], revit_script_util.Output)
            # make sure all subsequent data is appended to log file
            write_mode = "a"
    except Exception as e:
        output("test counter: {} failed with exception: {}".format(counter, e))
    output_header('completed test group: {}'.format(counter), revit_script_util.Output)
    counter = counter + 1

output_header("Executing tests.... finished ", revit_script_util.Output)
