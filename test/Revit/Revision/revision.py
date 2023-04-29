import sys

SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
sys.path += [SAMPLES_PATH]

from duHast.Revit.Revisions.revisions import (
    REVISION_DATA,
    create_revision,
    mark_revision_as_issued,
)
from duHast.Revit.Common.revit_version import get_revit_version_number

# import Autodesk
import Autodesk.Revit.DB as rdb

#: set up revision data for Revit up to version 2022
TEST_DATA_2022 = REVISION_DATA(
    description="unit test",
    issuedBy="tester",
    issuedTo="testy",
    revisionNumberType=rdb.RevisionNumberType.Numeric,
    revisionDate="23/12/23",
    tagCloudVisibility=False,
)

#: set up revision data for Revit from version 2023 onwards
TEST_DATA_2023 = REVISION_DATA(
    description="unit test",
    issuedBy="tester",
    issuedTo="testy",
    revisionNumberType="Numeric",
    revisionDate="23/12/23",
    tagCloudVisibility=False,
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
        assert result.result[0].IssuedTo == TEST_DATA_2022.issuedTo
        assert result.result[0].IssuedBy == TEST_DATA_2022.issuedBy
        assert result.result[0].RevisionDate == TEST_DATA_2022.revisionDate
        assert result.result[0].Visibility == TEST_DATA_2022.tagCloudVisibility
        assert result.result[0].NumberType == TEST_DATA_2022.revisionNumberType

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
        assert result.result[0].IssuedTo == TEST_DATA_2023.issuedTo
        assert result.result[0].IssuedBy == TEST_DATA_2023.issuedBy
        assert result.result[0].RevisionDate == TEST_DATA_2023.revisionDate
        assert result.result[0].Visibility == TEST_DATA_2023.tagCloudVisibility
        assert result.result[0].NumberType == TEST_DATA_2023.revisionNumberType

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
            result = mark_revision_as_issued(doc, result.result[0].id)
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
    # run test
    if revit_version <= 2022:
        flag, message = test_create_revision_pre_2023(doc)
        all_tests = all_tests & flag
        output("test_create_revision_pre_2023()", flag, message)
    else:
        flag, message = test_create_revision_2023(doc)
        all_tests = all_tests & flag
        output("test_create_revision_2023()", flag, message)

    flag, message = test_mark_revision_as_issued(doc)
    all_tests = all_tests & flag
    output("test_mark_revision_as_issued()", flag, message)

    flag, message = test_mark_revision_as_issued_by_id(doc)
    all_tests = all_tests & flag
    output("test_mark_revision_as_issued()", flag, message)

    return all_tests


if __name__ == "__main__":
    revit_version = get_revit_version_number(doc)
    if revit_version <= 2022:
        flag, message = test_create_revision_pre_2023(doc)
        all_tests = all_tests & flag
        print("test_create_revision_pre_2023()", flag, message)
    else:
        flag, message = test_create_revision_2023(doc)
        all_tests = all_tests & flag
        print("test_create_revision_2023()", flag, message)

    flag, message = test_mark_revision_as_issued(doc)
    all_tests = all_tests & flag
    print("test_mark_revision_as_issued()", flag, message)

    flag, message = test_mark_revision_as_issued_by_id(doc)
    all_tests = all_tests & flag
    print("test_mark_revision_as_issued_by_id()", flag, message)