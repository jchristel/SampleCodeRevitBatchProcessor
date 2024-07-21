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

# this sample moves revit link instances onto a workset specified in list

# --------------------------
# Imports
# --------------------------
import os.path
import settings as settings  # sets up all commonly used variables and path locations!

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
from test.Revit.Annotation.run_test_classes import run_annotation_tests
from test.Revit.Exports.run_test_classes import run_export_tests
from test.Revit.Family.run_test_classes import run_family_tests

#: add test runners to list
TESTS = [
    run_des_tests,
    run_rev_tests,
    run_view_tests,
    run_wall_tests,
    run_grids_tests,
    run_levels_tests,
    run_shared_parameters_tests,
    run_annotation_tests,
    run_export_tests,
    run_family_tests,
]

#: execute tests
output_header("Executing tests.... start", revit_script_util.Output)
#: test log file
file_name = os.path.join(
    settings.OUTPUT_FOLDER, get_file_name_without_ext(doc.Title) + ".csv"
)
#: overwrite previous test date at log file open
write_mode = "w"

counter = 0
for test in TESTS:
    output_header("starting test group: {}".format(counter), revit_script_util.Output)
    try:
        result = test(doc)
        # check if anything went wrong when attempting to marshall tests
        if result.status == False and len(result.result) == 0:
            output_header("Failed to marshall any tests", revit_script_util.Output)
            output(result.message, revit_script_util.Output)
        elif result.status == False and len(result.result) > 0:
            output_header("Failed to marshall all tests", revit_script_util.Output)
            output(result.message, revit_script_util.Output)
        # display and write out any messages from tests
        if len(result.result) > 0:
            for test_result in result.result:
                try:
                    # write results to file
                    write_report_data_as_csv(
                        file_name,
                        "",
                        [[test_result[3], test_result[4], test_result[5]]],
                        write_mode,
                    )
                except Exception as e:
                    output("Failed to write test report with exception: {}".format(e))
                # provide short summary only...more details in log file
                output(test_result[0], revit_script_util.Output)
                output(test_result[2], revit_script_util.Output)
                # make sure all subsequent data is appended to log file
                write_mode = "a"
    except Exception as e:
        output("test counter: {} failed with exception: {}".format(counter, e))
    output_header("completed test group: {}".format(counter), revit_script_util.Output)
    counter = counter + 1

output_header("Executing tests.... finished ", revit_script_util.Output)
