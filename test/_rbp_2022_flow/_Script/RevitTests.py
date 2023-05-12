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
from test.utils.rbp_setup import add_rbp_ref, output

# get the document from revit batch processor
doc = add_rbp_ref()

# flag whether this runs in debug or not
DEBUG = False

# -------------
# my code here:
# -------------

#: import test runners
from test.Revit.Revision.run_test_classes import run_revision_tests as run_rev_tests

#: add test runners to list
TESTS = [
    run_rev_tests,
]


#: execute tests
output("Executing tests.... start")

for test in TESTS:
    result = test(doc, True)
    output(result.message)

output("Executing tests.... finished ")
