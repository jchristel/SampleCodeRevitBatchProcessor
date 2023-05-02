"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit revision tests . 
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

from duHast.Revit.Revisions.revisions import (
    REVISION_DATA,
    create_revision,
    mark_revision_as_issued,
    mark_revision_as_issued_by_revision_id,
    get_issued_revisions,
    re_order_revisions,
)
from duHast.Revit.Common.revit_version import get_revit_version_number

from test.utils.transaction import in_transaction_group

# import Autodesk
import Autodesk.Revit.DB as rdb

#: set up revision data for Revit up to version 2022
TEST_DATA_2022 = REVISION_DATA(
    description="unit test",
    issued_by="tester",
    issued_to="testy",
    revision_number_type=rdb.RevisionNumberType.Numeric,
    revision_date="23/12/23",
    tag_cloud_visibility=rdb.RevisionVisibility.Hidden,
)

#: set up revision data for Revit from version 2023 onwards
TEST_DATA_2023 = REVISION_DATA(
    description="unit test",
    issued_by="tester",
    issued_to="testy",
    revision_number_type="Numeric",  # sequence name, which in turn defines the number type
    revision_date="23/12/23",
    tag_cloud_visibility=rdb.RevisionVisibility.Hidden,
)


def test_create_revision_pre_2023(doc):
    """
    Attempts to create a revision in revit versions prior to Revit 2023

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if revision was created successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"

    try:
        result = create_revision(doc, TEST_DATA_2022)
        message = " {} ".format(result)
        assert result.status == True
        assert len(result.result) == 1
        assert result.result[0].Description == TEST_DATA_2022.description
        assert result.result[0].IssuedTo == TEST_DATA_2022.issued_to
        assert result.result[0].IssuedBy == TEST_DATA_2022.issued_by
        assert result.result[0].RevisionDate == TEST_DATA_2022.revision_date
        assert result.result[0].Visibility == TEST_DATA_2022.tag_cloud_visibility
        assert result.result[0].NumberType == TEST_DATA_2022.revision_number_type

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_create_revision_pre_2023 {}".format(
                    e
                )
            )
        )
        flag = False

    return flag, message


def test_create_revision_2023(doc):
    """
    Attempts to create a revision in revit versions from Revit 2023 onwards

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if revision was created successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        result = create_revision(doc, TEST_DATA_2023)
        message = " {} ".format(result)
        assert result.status == True
        assert len(result.result) == 1
        assert result.result[0].Description == TEST_DATA_2023.description
        assert result.result[0].IssuedTo == TEST_DATA_2023.issued_to
        assert result.result[0].IssuedBy == TEST_DATA_2023.issued_by
        assert result.result[0].RevisionDate == TEST_DATA_2023.revision_date
        assert result.result[0].Visibility == TEST_DATA_2023.tag_cloud_visibility
        assert result.result[0].NumberType == TEST_DATA_2023.revision_number_type

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_create_revision_2023 {}".format(
                    e
                )
            )
        )
        flag = False
    return flag, message


def test_mark_revision_as_issued(doc):
    """
    mark_revision_as_issued test

    Creates a revision and then attempts to mark it as issued.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if revision was created successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"

    try:
        # check which revit version
        revit_version = get_revit_version_number(doc)
        result = None
        if revit_version <= 2022:
            result = create_revision(doc, TEST_DATA_2022)
        else:
            result = create_revision(doc, TEST_DATA_2023)

        if result.status:
            result = mark_revision_as_issued(doc, result.result[0])
            message = " {} ".format(result)
            assert result.status == True
        else:
            # throw an exception...
            assert result.status == True

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_mark_revision_as_issued {}".format(
                    e
                )
            )
        )
        flag = False

    return flag, message


def test_mark_revision_as_issued_by_id(doc):
    """
    mark_revision_as_issued_by_id test

    Creates a revision and then attempts to mark it as issued using the revision id provided.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if revision was created successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"

    try:
        # check which revit version
        revit_version = get_revit_version_number(doc)
        result = None
        if revit_version <= 2022:
            result = create_revision(doc, TEST_DATA_2022)
        else:
            result = create_revision(doc, TEST_DATA_2023)

        if result.status:
            result = mark_revision_as_issued_by_revision_id(doc, result.result[0].Id)
            message = " {} ".format(result)
            assert result.status == True
        else:
            # throw an exception...
            assert result.status == True

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_mark_revision_as_issued_by_id {}".format(
                    e
                )
            )
        )
        flag = False

    return flag, message


def test_get_issued_revisions(doc):
    """
    get_issued_revisions test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :raises ValueError: Any exception occurred in creating a revision or setting a revision to issued will be thrown again
    :raises ValueError: _description_
    :return: True if revision was created successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        # test model has no issued revisions to start with, check for empty:
        result = get_issued_revisions(doc)
        expected_result = []
        message = " {} ".format(result)
        assert result == expected_result

        # set up a revision , mark it as issued
        # check which revit version
        revit_version = get_revit_version_number(doc)
        if revit_version <= 2022:
            result = create_revision(doc, TEST_DATA_2022)
        else:
            result = create_revision(doc, TEST_DATA_2023)
        # check revision was created
        if result.status == False:
            raise ValueError(result.message)
        # mark revision as issued
        result = mark_revision_as_issued_by_revision_id(doc, result.result[0].Id)
        if result.status == False:
            raise ValueError(result.message)
        # check for issued revision again
        result = get_issued_revisions(doc)
        # there should be one issued revision in the model
        expected_result = 1
        message = message + "\n {} vs {}".format(len(result), expected_result)
        assert len(result) == expected_result

    except Exception as e:
        message = (
            message
            + "\n"
            + (
                "An exception occurred in function test_get_issued_revisions {}".format(
                    e
                )
            )
        )
        flag = False

    return flag, message


def _get_id_integers_from_list(my_list):
    """
    Returns a list representing the integer values of ids list past in.

    :param my_list: A list of element ids
    :type my_list: [Autodesk.Revit.DB.ElementId]
    :return: A list of integers
    :rtype: [int]
    """

    ids = []
    for item in my_list:
        ids.append(item.IntegerValue)
    return ids


def test_re_order_revisions(doc):
    """
    re_order_revisions test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :raises ValueError: Any exception occurred in creating a revision will be re-raised
    :return: True if revision was created successfully, otherwise False
    :rtype: Boolean
    """

    flag = True
    message = "-"
    try:
        # add another revision to model
        # check which revit version
        revit_version = get_revit_version_number(doc)
        if revit_version <= 2022:
            result = create_revision(doc, TEST_DATA_2022)
        else:
            result = create_revision(doc, TEST_DATA_2023)
        # check revision was created
        if result.status == False:
            raise ValueError(result.message)

        # get revisions in model
        revisions_in_model = rdb.Revision.GetAllRevisionIds(doc)
        # and reverse the list because thats what the end result should look like
        expected_result = list(reversed(revisions_in_model)).ToList[rdb.ElementId]()

        # apply new revisions order to model
        result = re_order_revisions(doc, expected_result)

        # get revisions now in the model
        revisions_in_model_re_ordered = rdb.Revision.GetAllRevisionIds(doc)

        message = "from result: {} vs expected: {} vs model: {}".format(
            _get_id_integers_from_list(result.result),
            _get_id_integers_from_list(expected_result),
            _get_id_integers_from_list(revisions_in_model_re_ordered),
        )
        # compare all three values
        assert _get_id_integers_from_list(result.result) == _get_id_integers_from_list(
            expected_result
        )
        assert _get_id_integers_from_list(result.result) == _get_id_integers_from_list(
            revisions_in_model_re_ordered
        )

    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function test_re_order_revisions {}".format(e))
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
    tests_2022 = [
        ["test_create_revision_2023", test_create_revision_pre_2023],
    ]
    # lists of tests to be executed from version revit 2023 onwards
    tests_2023 = [
        ["test_create_revision_2022", test_create_revision_2023],
    ]
    # lists of common tests ( not version specific )
    tests_common = [
        ["test_mark_revision_as_issued", test_mark_revision_as_issued],
        ["test_mark_revision_as_issued_by_id", test_mark_revision_as_issued_by_id],
        ["test_get_issued_revisions", test_get_issued_revisions],
        ["test_re_order_revisions", test_re_order_revisions],
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
