"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit sheet views report tests . 
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

import sys, os
import clr
import tempfile

# require for ToList()
clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# add additional path
TEST_PATH = ""
SAMPLES_PATH = ""
# check if __file__ is defined. Not the case when running this in the revit python shell
# should work in batch processor!
try:
    # __file__ is defined
    TEST_PATH = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    )
    SAMPLES_PATH = os.path.join(TEST_PATH, r"duHast\src")
except:
    # __file__ is not defined, add manual path to repo. Not sure whether there is a better way...
    SAMPLES_PATH = (
        r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
    )
    TEST_PATH = r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor"

sys.path += [SAMPLES_PATH, TEST_PATH]

from duHast.Revit.Views.Reporting.sheets_report import (
    get_sheet_report_data,
    get_sheets_report_data_filtered,
    write_sheet_data,
    write_sheet_data_by_property_names,
)
from duHast.Revit.Common.revit_version import get_revit_version_number

from test.utils.transaction import in_transaction_group
from test.Revit.Views.utils import report_tests as rep_test


# import Autodesk
import Autodesk.Revit.DB as rdb

#: the test file name to be used in reports
REVIT_TEST_FILE_NAME = "TEST.rvt"

#: file name of report file
OUTPUT_FILE_NAME = "Report.csv"

# These are the properties to be reported on in filtered reports
VIEW_DATA_FILTERS = ["View Name", "Title on Sheet", "View Template"]


def test_get_sheet_report_data(doc):
    """
    get sheet report data test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if tested successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        result = get_sheet_report_data(doc, REVIT_TEST_FILE_NAME)
        expected_result = [
            [
                REVIT_TEST_FILE_NAME,
                "970427",
                "-1",
                "Level 00",
                "Independent",
                "None",
                " 1 : 100",
                "100",
                "Normal",
                "Coarse",
                "Show Original",
                "None",
                "None",
                "No",
                "No",
                "No",
                "Invalid storage type: (NONE)",
                "Invalid storage type: (NONE)",
                "-1",
                "-1",
                "Look down",
                "Invalid storage type: (NONE)",
                "Level 00",
                "Project North",
                "2029",
                "3",
                "Clean all wall joins",
                "-1",
                "Architectural",
                "By Discipline",
                "Background",
                "Invalid storage type: (NONE)",
                "-1",
                "None",
                "-1",
                "None",
                "None",
                "None",
                "970435",
                "No",
            ],
            [
                REVIT_TEST_FILE_NAME,
                "21930",
                "-1",
                "TEST",
                "Independent",
                "None",
                " 1 : 1",
                "1",
                "Medium",
                "None",
                "None",
                "Invalid storage type: (NONE)",
                "Architectural",
                "TEST",
                "None",
                "TEST",
                "21935",
                "Hidden Line",
            ],
        ]
        message = " result: {} \n expected: {} ".format(result, expected_result)
        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_sheet_report_data {}".format(
                    e
                )
            )
        )
        flag = False
    return flag, message


def test_get_sheets_report_data_filtered(doc):
    """
    get sheets report data filtered test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if tested successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        result = get_sheets_report_data_filtered(
            doc, REVIT_TEST_FILE_NAME, VIEW_DATA_FILTERS
        )
        expected_result = [
            [REVIT_TEST_FILE_NAME, "970427", "Level 00", "None", "-1"],
            [REVIT_TEST_FILE_NAME, "21930", "TEST", "None", "-1"],
        ]
        message = " result: {} \n expected: {} ".format(result, expected_result)
        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_sheets_report_data_filtered {}".format(
                    e
                )
            )
        )
        flag = False
    return flag, message


def test_write_sheets_data(doc):
    """
    Write all sheet data test.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if tested successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        # set up a temp dir and test file path
        tmp_dir = tempfile.mkdtemp()
        test_file_path = os.path.join(tmp_dir, OUTPUT_FILE_NAME)

        # attempt to write out data
        result = write_sheet_data(
            doc, os.path.join(tmp_dir, "sheets_test.txt"), REVIT_TEST_FILE_NAME
        )
        message = " file written: {} to: {}".format(result.status, result.message)
        # check file was written
        assert result.status == True

        # double check...
        expected_result_file_read = []
        # check file content and perform temp directory clean up
        flag_clean_up, message_clean_up = rep_test.check_csv_file(
            test_file_path, expected_result_file_read, tmp_dir, "test_write_sheets_data"
        )
        flag = flag & flag_clean_up
        message = message + "\n" + message_clean_up

    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_write_sheet_data {}".format(e))
        )
        flag = False
    return flag, message


def test_write_sheet_data_by_property_names(doc):
    """
    Write sheet data with property filter test.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if tested successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        # set up a temp dir and test file path
        tmp_dir = tempfile.mkdtemp()
        test_file_path = os.path.join(tmp_dir, OUTPUT_FILE_NAME)

        # attempt to write out data
        result = write_sheet_data_by_property_names(
            doc,
            os.path.join(tmp_dir, "sheets_test.txt"),
            REVIT_TEST_FILE_NAME,
            VIEW_DATA_FILTERS,
        )
        message = " file written: {} to: {}".format(result.status, result.message)
        # check file was written
        assert result.status == True

        # double check...
        expected_result_file_read = []
        # check file content and perform temp directory clean up
        flag_clean_up, message_clean_up = rep_test.check_csv_file(
            test_file_path, expected_result_file_read, tmp_dir, "test_write_sheets_data_by_property_name"
        )
        flag = flag & flag_clean_up
        message = message + "\n" + message_clean_up

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_write_sheet_data_by_property_names {}".format(
                    e
                )
            )
        )
        flag = False
    return flag, message


def run_tests(doc, output):
    """
    Runs all tests in this module

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: A function to direct any output to.
    :type output: fun(message)
    :return: True if all tests returned True, otherwise False
    :rtype: boolean
    """

    all_tests = True
    # check which revit version
    revit_version = get_revit_version_number(doc)

    # lists of tests to be executed up to version revit 2022
    tests_2022 = []
    # lists of tests to be executed from version revit 2023 onwards
    tests_2023 = []
    # lists of common tests ( not version specific )
    tests_common = [
        ["test_get_sheet_report_data", test_get_sheet_report_data],
        ["test_get_sheets_report_data_filtered", test_get_sheets_report_data_filtered],
        ["test_write_sheets_data", test_write_sheets_data],
        [
            "test_write_sheet_data_by_property_names",
            test_write_sheet_data_by_property_names,
        ],
    ]

    # check which version specific tests to execute
    by_version_tests = []
    if revit_version <= 2022:
        by_version_tests = tests_2022
    else:
        by_version_tests = tests_2023

    # run version specific tests
    for test in by_version_tests:
        flag, message = in_transaction_group(doc, test[1])
        all_tests = all_tests & flag
        output(test[0], flag, message)

    # run common tests
    for test in tests_common:
        flag, message = in_transaction_group(doc, test[1])
        all_tests = all_tests & flag
        output(test[0], flag, message)

    return all_tests


if __name__ == "__main__":
    # in line function to print
    def action(function, flag, message):
        print("{} [{}]".format(function, flag))
        print(message)

    run_tests(doc, action)
