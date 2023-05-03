import sys, os

#: path to samples library in repository
SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
#: path to test directory in repository
TEST_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path += [SAMPLES_PATH, TEST_PATH]

from Utility.temp_files_dirs import write_test_files, call_with_temp_directory

from duHast.Utilities.directory_io import (
    directory_exists,
)

def run_tests(output):
    """
    Runs all tests in this module

    :param output: A function to direct any output to.
    :type output: fun(message)
    :return: True if all tests returned True, otherwise False
    :rtype: boolean
    """

    all_tests = True

    # lists of tests to be executed
    tests = [
        
    ]

    tests_temp_files = [
        
    ]

    # execute tests
    for test in tests:
        flag, message = test[1]()
        all_tests = all_tests & flag
        output(test[0], flag, message)

    # exec tests requiring a temp directory
    for test in tests_temp_files:
        flag, message = call_with_temp_directory(test[1])
        all_tests = all_tests & flag
        output(test[0], flag, message)

    return all_tests


if __name__ == "__main__":
    # in line function to print
    def action(function, flag, message):
        print("{} [{}]".format(function, flag))
        print(message)

    run_tests(action)