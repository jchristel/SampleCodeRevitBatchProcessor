"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit design set and options tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Assumes model has 

Two design sets with a total of 3 design options.

- Design Set 1

    - Option 1
    - Option 2 (primary)

- Design Set 2

    - Option 1 (primary)

 
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

SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
TEST_PATH = r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor"
sys.path += [SAMPLES_PATH, TEST_PATH]

from duHast.Revit.Common.design_set_options import get_design_options, get_design_sets

from duHast.Revit.Common.revit_version import get_revit_version_number

from test.utils.transaction import in_transaction_group


# import Autodesk
import Autodesk.Revit.DB as rdb

DESIGN_OPTION_DATA = [
    ["Option 1", "Option Set 1", False],
    ["Option 2", "Option Set 1", True],
    ["Option 1", "Option Set 2", True],
]

def _strip_primary(option_name):
    '''
    Strips anything after ' <' from an option name. ie. <primary> if in option name. Otherwise the name will be returned unchanged.

    :param option_name: The design option name.
    :type option_name: str
    :return: Option name without the primary indicator
    :rtype: str
    '''

    if("<" in option_name):
        option_name = option_name[:option_name.index("<")-2]
    return option_name

def test_get_design_options(doc):
    """
    get design options test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if design options where retrieved successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"

    try:
        result_sets = get_design_options(doc)
        # get the option names only
        result = list([_strip_primary(rdb.Element.Name.GetValue(entry)) for entry in result_sets])
        # get all option names
        expected_result = list(do[0] for do in DESIGN_OPTION_DATA)
        message = " {} vs {}".format(sorted(result), sorted(expected_result))

        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_get_design_options {}".format(e))
        )
        flag = False

    return flag, message


def test_get_design_sets(doc):
    """
    get design sets test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if design options where retrieved successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"

    try:
        result_sets = get_design_sets(doc)
        # get the set names only
        result = list(rdb.Element.Name.GetValue(entry) for entry in result_sets)
        # get a unique list of design set names
        expected_result = list(set(do[1] for do in DESIGN_OPTION_DATA))
        message = " {} vs {}".format(sorted(result), sorted(expected_result))

        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_get_design_sets {}".format(e))
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
        ["test_get_design_options", test_get_design_options],
        ["test_get_design_sets", test_get_design_sets],
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
