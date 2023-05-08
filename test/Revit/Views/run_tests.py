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

import sys

SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
TEST_PATH = r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor"
TEST_PATH_TEST = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\test"
)
sys.path += [SAMPLES_PATH, TEST_PATH, TEST_PATH_TEST]


from test.utils.rbp_setup import add_rbp_ref, output as rbp_out

from test.Revit.Views.views import run_tests as view_run_test
from test.Revit.Views.views_report import run_tests as report_run_test
from test.Revit.Views.views_report_header import run_tests as report_header_run_test
from test.Revit.Views.views_sheets_report import run_tests as report_sheets_run_test
from test.Revit.Views.views_schedule_report import run_tests as report_schedules_run_test

from test.utils.padding import pad_header_no_time_stamp, pad_string

#: Type of test run flag. If False run in revit python shell. If True runs in revit batch processor.
IS_RBP_RUN = False


def run_view_tests(doc, rbp_run_type=IS_RBP_RUN):
    """
    Runs all views related tests.

    :param doc: Current Revit document.
    :type doc: Autodesk.Revit.DB.Document

    :return: True if all tests completed successfully, otherwise False.
    :rtype: bool
    """

    output_function = out
    output_function_header = out_header
    if rbp_run_type == True:
        # add revit batch processor references and get the current document
        doc = add_rbp_ref()
        output_function = rbp_out
        output_function_header = rbp_out

    #: overall test status
    overall_status = True

    # start tests -> should run view tests first since they form
    # part of other view related tests

    tests = [
        ["Views", view_run_test],
        ["view report headers", report_header_run_test],
        ["view reports", report_run_test],
        ["sheet reports", report_sheets_run_test],
        ["report_schedules_run_test",report_schedules_run_test]
    ]

    for test in tests:
        output_function_header(pad_header_no_time_stamp(test[0]))
        result = test[1](doc, output_function)
        overall_status = overall_status & result

    return overall_status


def out_header(header):
    """
    Just prints header.

    :param header: A header line.
    :type header: str
    """

    print(header)


def out(func_name, result_flag, message):
    """
    print messages to screen when debugging

    :param func_name: The function tested name.
    :type func_name: str
    :param result_flag: True if test completed successfully, otherwise False
    :type result_flag: bool
    :param message: Any debug message coming back from the test function.
    :type message: str
    """

    message_short = "{} [{}]".format(func_name, result_flag)
    print(pad_string(message_short))
    if IS_RBP_RUN:
        print(pad_string(message))


if __name__ == "__main__":
    run_view_tests(doc)
