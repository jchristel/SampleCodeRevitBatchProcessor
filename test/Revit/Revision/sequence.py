import sys

SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
sys.path += [SAMPLES_PATH]

from duHast.Revit.Revisions.sequence import (
    get_revision_seq_of_name,
    create_revision_alpha_seq,
)

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
    '''
    Runs all tests in this module

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: A function to direct any output to.
    :type output: fun(message)
    :return: True if all tests returned True, otherwise False
    :rtype: boolean
    '''

    all_tests = True

    flag, message = test_create_revision_alpha_seq(doc)
    all_tests = all_tests & flag
    output("test_create_revision_alpha_seq()", flag, message)

    flag, message = test_get_revision_seq_of_name(doc)
    all_tests = all_tests & flag
    output("test_get_revision_seq_of_name()", flag, message)

    return all_tests



if __name__ == "__main__":
    flag, message = test_create_revision_alpha_seq(doc)
    print("test_create_revision_alpha_seq() [{}]".format(flag))
    print(message)

    flag, message = test_get_revision_seq_of_name(doc)
    print("get_revision_seq_of_name() [{}]".format(flag))
    print(message)
