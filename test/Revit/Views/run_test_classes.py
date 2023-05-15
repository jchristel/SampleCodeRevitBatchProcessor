"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module runs all revit views related tests . 
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
from duHast.Utilities import result as res

# import test classes
from test.Revit.Views import views_get
from test.Revit.Views import views_get_types

from test.Revit.Views import sheets_get_report_headers
from test.Revit.Views import schedules_get_report_headers
from test.Revit.Views import views_get_report_headers

from test.Revit.Views import views_get_report_data
from test.Revit.Views import views_get_report_data_filtered
from test.Revit.Views import views_write_report_data
from test.Revit.Views import views_write_report_data_filtered


def run_views_tests(doc):
    """
    Runs all views related tests.

    :param doc: Current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True if all tests completed successfully, otherwise False.
    :rtype: bool
    """

    return_value = res.Result()

    # start tests -> should run report header tests first since they form
    # part of report tests

    run_tests = [
        ["Get Sheets Report Header", sheets_get_report_headers.GetSheetReportHeaders],
        [
            "Get Schedule Report Header",
            schedules_get_report_headers.GetScheduleReportHeaders,
        ],
        ["Get Views Report Header", views_get_report_headers.GetViewReportHeaders],
        ["Get Views", views_get.GetViews],
        ["Get View Types", views_get_types.GetViewTypes],
        ["Get Views Report Data", views_get_report_data.GetViewReportData],
        [
            "Get Views Report Data Filtered",
            views_get_report_data_filtered.GetViewReportDataFiltered,
        ],
        ["Write Views Report Data", views_write_report_data.WriteViewReportData],
        [
            "Write Views Report Data Filtered",
            views_write_report_data_filtered.WriteViewReportDataFiltered,
        ],
    ]

    runner = RevitRunTest(run_tests)
    return_value = runner.run_tests(doc)

    return return_value
