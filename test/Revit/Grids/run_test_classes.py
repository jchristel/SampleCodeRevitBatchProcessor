"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module runs all revit grids related tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
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


from test.Revit.TestUtils.run_revit_tests import RevitRunTest
from duHast.Utilities.Objects import result as res

# import test classes
from test.Revit.Grids import grids_get_report_data
from test.Revit.Grids import grids_two_d, grids_show_bubble_end, grids_toggle_bubble_end_one, grids_toggle_bubble_end_zero



def run_grids_tests(doc):
    """
    Runs all grids related tests.

    :param doc: Current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True if all tests completed successfully, otherwise False.
    :rtype: bool
    """

    return_value = res.Result()

    # start tests -> should run ... tests first since they form
    # part of ... tests

    run_tests = [
        ["Get Grids Report Data", grids_get_report_data.GetGridReportData],
        ["grids to 2D", grids_two_d.GridsTwoD],
        ["Toggle Grid Bubbles", grids_show_bubble_end.GridsToggleBubbleVisibilityAtEnd],
        ["Toggle Grid Bubbles Zero End", grids_toggle_bubble_end_zero.GridsToggleBubbleVisibilityAtZeroEnd],
        ["Toggle Grid Bubbles One End", grids_toggle_bubble_end_one.GridsToggleBubbleVisibilityAtOneEnd],
    ]

    runner = RevitRunTest(run_tests)
    return_value = runner.run_tests(doc)

    return return_value
