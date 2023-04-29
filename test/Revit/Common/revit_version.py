import sys

SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
sys.path += [SAMPLES_PATH]

from duHast.Revit.Common.revit_version import get_revit_version_number


def test_get_revit_version_number(doc):
    '''
    get_revit_version_number test

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: True if all tests pass, otherwise False
    :rtype: bool
    '''

    flag = True
    message = '-'
    try:
        expected_result = 2022
        result = get_revit_version_number(doc)
        message = (' {} vs {}'.format(result, expected_result))
        assert result == expected_result
    except Exception as e:
        message = message + '\n' + ('An exception occurred in function test_get_revit_version_number {}'.format(e))
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
    flag, message = test_get_revit_version_number(doc)
    all_tests = all_tests & flag
    output("test_get_revit_version_number()", flag, message)

    return all_tests


if __name__ == "__main__":
    flag, message = test_get_revit_version_number(doc)
    print('test_get_revit_version_number() [{}]'.format(flag))
    print(message)
