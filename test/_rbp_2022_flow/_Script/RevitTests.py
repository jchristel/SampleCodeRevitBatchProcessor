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
import utilRevitTests as utilM  # sets up all commonly used variables and path locations!

# get document and import revit batch processor
from test.utils.rbp_setup import add_rbp_ref
from duHast.Utilities.console_out import output, output_header
import revit_script_util

# get the document from revit batch processor
doc = add_rbp_ref()

# flag whether this runs in debug or not
DEBUG = False

# -------------
# my code here:
# -------------

#: import test runners
from test.Revit.Common.run_test_classes import run_design_set_options_tests as run_des_tests
from test.Revit.Revision.run_test_classes import run_revision_tests as run_rev_tests
from test.Revit.Views.run_test_classes import run_views_tests as run_view_tests
from test.Revit.Walls.run_test_classes import run_walls_tests as run_wall_tests

#: add test runners to list
TESTS = [
    run_des_tests,
    run_rev_tests,
    run_view_tests,
    run_wall_tests,
]


#: execute tests
output_header("Executing tests.... start", revit_script_util.Output)

for test in TESTS:
    result = test(doc)
    for test_result in result.result:
        # if everything went well just provide a summary
        if(test_result[1].status):
            output(test_result[0],revit_script_util.Output)
            output(test_result[2],revit_script_util.Output)
        else:
            # something went wrong...provide details
            output(test_result[0], revit_script_util.Output)
            output(test_result[1].message, revit_script_util.Output)
            output(test_result[2], revit_script_util.Output)


output_header("Executing tests.... finished ", revit_script_util.Output)
