"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit views tests . 
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

from duHast.Revit.Views.views import (
    get_views_in_model,
    get_view_types,
)

from duHast.Revit.Common.revit_version import get_revit_version_number

from test.utils.transaction import in_transaction_group

# import Autodesk
import Autodesk.Revit.DB as rdb


def test_get_view_types(doc):
    """
    test get view types

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if tested successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        expected_result = [
            ["Structural Plan", rdb.ViewFamily.StructuralPlan],
            ["3D View", rdb.ViewFamily.ThreeDimensional],
            ["Schedule", rdb.ViewFamily.Schedule],
            ["Sheet", rdb.ViewFamily.Sheet],
            ["Walkthrough", rdb.ViewFamily.Walkthrough],
            ["Rendering", rdb.ViewFamily.ImageView],
            ["Cost Report", rdb.ViewFamily.CostReport],
            ["Legend", rdb.ViewFamily.Legend],
            ["Loads Report", rdb.ViewFamily.LoadsReport],
            ["Pressure Loss Report", rdb.ViewFamily.PressureLossReport],
            ["Panel Schedule", rdb.ViewFamily.PanelSchedule],
            ["Graphical Column Schedule", rdb.ViewFamily.GraphicalColumnSchedule],
            ["STC & NOTES", rdb.ViewFamily.Drafting],
            ["RCP (B53 Series)", rdb.ViewFamily.CeilingPlan],
            ["Section (D Series)", rdb.ViewFamily.Section],
            ["Plan Site (A Series)", rdb.ViewFamily.FloorPlan],
            ["NLA", rdb.ViewFamily.AreaPlan],
            ["DETAIL INTERIOR (J SERIES)", rdb.ViewFamily.Detail],
            ["Elevation (C Series)", rdb.ViewFamily.Elevation],
            ["Analysis Report", rdb.ViewFamily.SystemsAnalysisReport],
        ]
        result_col = get_view_types(doc)
        result = []
        for vt in result_col:
            result.append([rdb.Element.Name.GetValue(vt), vt.ViewFamily])
        message = " {} vs \n {}".format(result, expected_result)
        assert sorted(result) == sorted(expected_result)
    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_get_view_types {}".format(e))
        )
        flag = False
    return flag, message


def test_get_views_in_model(doc):
    """
    get views in model test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if tested successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        # set up a return all views filter
        def action(x):
            return True

        # get all views in model (only 1 in test model)
        result = get_views_in_model(doc, action)
        message = " view name: {}, view type: {}, ".format(
            result[0].Name, result[0].ViewType
        )
        assert result[0].Name == "TEST"
        assert result[0].ViewType == rdb.ViewType.DraftingView

        message = message + "\n" + " view name: {}, view type: {} ".format(
            result[1].Name, result[1].ViewType
        )
        assert result[1].ViewType == rdb.ViewType.Schedule
        assert result[1].Name == 'Wall Schedule'

        message = message + "\n" + " view name: {}, view type: {} ".format(
            result[2].Name, result[2].ViewType
        )
        assert result[2].ViewType == rdb.ViewType.FloorPlan
        assert result[2].Name=='Level 00'
        assert len(result) == 3

    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_get_views_in_model {}".format(e))
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
        ["test_get_views_in_model", test_get_views_in_model],
        ["test_get_view_types", test_get_view_types],
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
