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
# BSD License
# Copyright © 2023, Jan Christel
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


from test.Revit.TestUtils.run_revit_tests import RevitRunTest
from duHast.Utilities.Objects import result as res

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

from test.Revit.Views import schedules_get_report_data
from test.Revit.Views import schedules_get_report_data_filtered
from test.Revit.Views import schedules_write_report_data
from test.Revit.Views import schedules_write_report_data_filtered

from test.Revit.Views import sheets_get_report_data
from test.Revit.Views import sheets_get_report_data_filtered
from test.Revit.Views import sheets_write_report_data
from test.Revit.Views import sheets_write_report_data_filtered


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
        ["Get Schedules Report Data", schedules_get_report_data.GetScheduleReportData],
        [
            "Get Schedules Report Data Filtered",
            schedules_get_report_data_filtered.GetScheduleReportDataFiltered,
        ],
        ["Write Schedules Report Data", schedules_write_report_data.WriteScheduleReportData],
        [
            "Write Schedules Report Data Filtered",
            schedules_write_report_data_filtered.WriteScheduleReportDataFiltered
        ],
        ["Get Sheets Report Data", sheets_get_report_data.GetSheetReportData],
        [
            "Get Sheets Report Data Filtered",
            sheets_get_report_data_filtered.GetSheetReportDataFiltered,
        ],
        ["Write Sheets Report Data", sheets_write_report_data.WriteSheetReportData],
        [
            "Write Sheets Report Data Filtered",
            sheets_write_report_data_filtered.WriteSheetReportDataFiltered
        ],
    ]

    runner = RevitRunTest(run_tests)
    return_value = runner.run_tests(doc)

    return return_value
