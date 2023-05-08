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

from duHast.Revit.Views.Reporting.schedules_report import (
    get_schedules_report_data,
    get_schedules_report_data_filtered,
    write_schedule_data,
    write_schedule_data_by_property_names,
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
VIEW_DATA_FILTERS = ["View Name", "View Template"]


def test_get_schedules_report_data(doc):
    """
    get schedules report data test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if tested successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        result = get_schedules_report_data(doc, REVIT_TEST_FILE_NAME)
        expected_result = [
            [
                "TEST.rvt",
                "970420",
                "-1",
                "Wall Schedule",
                "Independent",
                "Invalid storage type: (NONE)",
                "2029",
                "3",
                "Invalid storage type: (NONE)",
                "Invalid storage type: (NONE)",
                "Invalid storage type: (NONE)",
                "Invalid storage type: (NONE)",
                "Invalid storage type: (NONE)",
                "None",
                "-1",
            ]
        ]
        message = " result: {} \n expected: {} ".format(result, expected_result)
        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_schedules_report_data {}".format(
                    e
                )
            )
        )
        flag = False
    return flag, message


def test_get_schedules_report_data_filtered(doc):
    """
    get schedules report data filtered test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if tested successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        result = get_schedules_report_data_filtered(
            doc, REVIT_TEST_FILE_NAME, VIEW_DATA_FILTERS
        )
        expected_result = [["TEST.rvt", "970420", "Wall Schedule", "-1"]]
        message = " result: {} \n expected: {} ".format(result, expected_result)
        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_schedules_report_data_filtered {}".format(
                    e
                )
            )
        )
        flag = False
    return flag, message


def test_write_schedules_data(doc):
    """
    Write all schedules data test.

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
        result = write_schedule_data(doc, test_file_path, REVIT_TEST_FILE_NAME)
        message = " file written: {} to: {}".format(result.status, result.message)
        # check file was written
        assert result.status == True

        # double check...
        expected_result_file_read = [
            [
                "HOSTFILE",
                "Id",
                "View Template",
                "View Name",
                "Dependency",
                "Visibility/Graphics Overrides",
                "Phase Filter",
                "Phase",
                "Fields",
                "Filter",
                "Sorting/Grouping",
                "Formatting",
                "Appearance",
                "Design Stage",
                "None",
            ],
            [
                "TEST.rvt",
                "970420",
                "-1",
                "Wall Schedule",
                "Independent",
                "Invalid storage type: (NONE)",
                "2029",
                "3",
                "Invalid storage type: (NONE)",
                "Invalid storage type: (NONE)",
                "Invalid storage type: (NONE)",
                "Invalid storage type: (NONE)",
                "Invalid storage type: (NONE)",
                "None",
                "-1",
            ],
        ]
        # check file content and perform temp directory clean up
        flag_clean_up, message_clean_up = rep_test.check_csv_file(
            test_file_path,
            expected_result_file_read,
            tmp_dir,
            "test_write_schedules_data",
        )
        flag = flag & flag_clean_up
        message = message + "\n" + message_clean_up

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_write_schedules_data {}".format(
                    e
                )
            )
        )
        flag = False
    return flag, message


def test_write_schedule_data_by_property_names(doc):
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
        result = write_schedule_data_by_property_names(
            doc,
            test_file_path,
            REVIT_TEST_FILE_NAME,
            VIEW_DATA_FILTERS,
        )
        message = " file written: {} to: {}".format(result.status, result.message)
        # check file was written
        assert result.status == True

        # double check...
        expected_result_file_read = [
            ["HOSTFILE", "Id", "View Name", "View Template"],
            ["TEST.rvt", "970420", "Wall Schedule", "-1"],
        ]
        # check file content and perform temp directory clean up
        flag_clean_up, message_clean_up = rep_test.check_csv_file(
            test_file_path,
            expected_result_file_read,
            tmp_dir,
            "test_write_schedule_data_by_property_names",
        )
        flag = flag & flag_clean_up
        message = message + "\n" + message_clean_up

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_write_schedule_data_by_property_names {}".format(
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
        ["test_get_schedules_report_data", test_get_schedules_report_data],
        [
            "test_get_schedules_report_data_filtered",
            test_get_schedules_report_data_filtered,
        ],
        ["test_write_schedules_data", test_write_schedules_data],
        [
            "test_write_schedule_data_by_property_names",
            test_write_schedule_data_by_property_names,
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
