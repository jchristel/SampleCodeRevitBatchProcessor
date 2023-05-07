"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit views report tests . 
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

from duHast.Revit.Views.Reporting.views_report_header import (
    get_sheets_report_headers,
    get_schedules_report_headers,
    get_views_report_headers,
)

from duHast.Revit.Common.revit_version import get_revit_version_number

from test.utils.transaction import in_transaction_group

# import Autodesk
import Autodesk.Revit.DB as rdb


def test_get_sheets_report_headers(doc):
    """
    get sheets report header test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if tested successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        # get sheet report headers
        result = get_sheets_report_headers(doc)
        expected_result = [
            "HOSTFILE",
            "Id",
            "Dependency",
            "Referencing Sheet",
            "Referencing Detail",
            "Visibility/Graphics Overrides",
            "Current Revision Issued",
            "Current Revision Issued By",
            "Current Revision Issued To",
            "Current Revision Date",
            "Current Revision Description",
            "Current Revision",
            "File Path",
            "Approved By",
            "Designed By",
            "Checked By",
            "Drawn By",
            "Scale",
            "Sheet Number",
            "Sheet Name",
            "Sheet Issue Date",
            "Design Stage",
            "View Type",
            "None",
            "Appears In Sheet List",
            "Revisions on Sheet",
            "Guide Grid",
        ]
        message = " result: {} \n expected: {} ".format(result, expected_result)
        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_sheets_report_headers {}".format(
                    e
                )
            )
        )
        flag = False
    return flag, message


def test_get_schedules_report_headers(doc):
    """
    get schedules report header test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if tested successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        # get sheet report headers
        result = get_schedules_report_headers(doc)
        expected_result = [
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
        ]
        message = " result: {} \n expected: {} ".format(result, expected_result)
        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_schedules_report_headers {}".format(
                    e
                )
            )
        )
        flag = False
    return flag, message


def test_get_views_report_headers(doc):
    """
    get views report header test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if tested successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        # get sheet report headers
        result = get_views_report_headers(doc)
        expected_result = [
            "HOSTFILE",
            "Id",
            "View Template",
            "View Name",
            "Dependency",
            "Title on Sheet",
            "View Scale",
            "Scale Value    1:",
            "Display Model",
            "Detail Level",
            "Parts Visibility",
            "Referencing Sheet",
            "Referencing Detail",
            "Crop View",
            "Crop Region Visible",
            "Annotation Crop",
            "Visibility/Graphics Overrides",
            "Graphic Display Options",
            "Range: Base Level",
            "Range: Top Level",
            "Underlay Orientation",
            "View Range",
            "Associated Level",
            "Orientation",
            "Phase Filter",
            "Phase",
            "Wall Join Display",
            "Scope Box",
            "Discipline",
            "Show Hidden Lines",
            "Color Scheme Location",
            "Color Scheme",
            "Default Analysis Display Style",
            "Depth Clipping",
            "Visible In Option",
            "Design Stage",
            "Building",
            "View Type",
            "None",
            "Sun Path",
        ]
        message = " result: {} \n expected: {} ".format(result, expected_result)
        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_views_report_headers {}".format(
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
        ["test_get_sheets_report_headers", test_get_sheets_report_headers],
        ["test_get_schedules_report_headers", test_get_schedules_report_headers],
        ["test_get_views_report_headers", test_get_views_report_headers],
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
