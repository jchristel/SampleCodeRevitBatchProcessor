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


from test.utils.rbp_setup import add_rbp_ref
from test.utils.padding import pad_header_no_time_stamp, pad_string
from duHast.Utilities import result as res

# import test classes
from test.Revit.Views import sheets_get_report_headers
from test.Revit.Views import schedules_get_report_headers
from test.Revit.Views import views_get_report_headers

from test.Revit.Views import views_get_report_data
from test.Revit.Views import views_get_report_data_filtered

#: Type of test run flag. If False run in revit python shell. If True runs in revit batch processor.
IS_RBP_RUN = False


def run_views_tests(doc, rbp_run_type=IS_RBP_RUN):
    """
    Runs all views related tests.

    :param doc: Current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True if all tests completed successfully, otherwise False.
    :rtype: bool
    """

    return_value = res.Result()
    if rbp_run_type == True:
        # add revit batch processor references and get the current document
        doc = add_rbp_ref()

    # start tests -> should run report header tests first since they form
    # part of report tests

    run_tests = [
        ["Get Sheets Report Header", sheets_get_report_headers.GetSheetReportHeaders],
        ["Get Schedule Report Header", schedules_get_report_headers.GetScheduleReportHeaders],
        ["Get Views Report Header", views_get_report_headers.GetViewReportHeaders],
        ["Get Views Report Data", views_get_report_data.GetViewReportData],
        ["Get Views Report Data Filtered", views_get_report_data_filtered.GetViewReportDataFiltered]
    ]

    for test in run_tests:
        return_value.append_message(pad_header_no_time_stamp(test[0]))
        test_class = test[1](doc)
        result_test = test_class.test()
        return_value.update(result_test)
        return_value.append_message(
            pad_string("{} completed status [{}]".format(test[0], result_test.status))
        )

    return return_value
