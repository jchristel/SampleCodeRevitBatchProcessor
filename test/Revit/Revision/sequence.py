"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit revision sequence tests . 
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
sys.path += [SAMPLES_PATH, TEST_PATH]

from duHast.Revit.Revisions.sequence import (
    get_revision_seq_of_name,
    create_revision_alpha_seq,
)

from test.utils.transaction import in_transaction_group

ALPHA_SEQUENCE_NAME = "alpha_test_sequence"


def test_create_revision_alpha_seq(doc):
    """
    create_revision_alpha_seq test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if all tests pass, otherwise False
    :rtype: bool
    """

    flag = True
    message = "-"
    try:
        # create a mock revision sequence
        expected_result = ALPHA_SEQUENCE_NAME
        result = create_revision_alpha_seq(doc, expected_result)
        message = " {} vs {}".format(result.Name, expected_result)
        assert result.Name == expected_result
    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_create_revision_alpha_seq {}".format(
                    e
                )
            )
        )
        flag = False
    return flag, message


def test_get_revision_seq_of_name(doc):
    """
    get_revision_seq_of_name test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if all tests pass, otherwise False
    :rtype: bool
    """

    flag = True
    message = "-"
    try:
        # create sequence
        create_revision_alpha_seq(doc, ALPHA_SEQUENCE_NAME)

        # get sequence by name
        result = get_revision_seq_of_name(doc, ALPHA_SEQUENCE_NAME)
        message = " {} vs {}".format(result.Name, ALPHA_SEQUENCE_NAME)
        assert result.Name == ALPHA_SEQUENCE_NAME

        # test missing sequence
        result = get_revision_seq_of_name(doc, "Missing Sequence")
        message = " {} vs {}".format(result, None)
        assert result == None

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function get_revision_seq_of_name {}".format(
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

    flag, message = in_transaction_group(doc, test_create_revision_alpha_seq)
    all_tests = all_tests & flag
    output("test_create_revision_alpha_seq()", flag, message)

    flag, message = in_transaction_group(doc, test_get_revision_seq_of_name)
    all_tests = all_tests & flag
    output("test_get_revision_seq_of_name()", flag, message)

    return all_tests


if __name__ == "__main__":

    # in line function to print
    def action(function, flag, message):
        print('{} [{}]'.format(function, flag))
        print(message)

    run_tests(doc, action)
