import os
from datetime import datetime


import sys

SAMPLES_PATH = (
    r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
)
sys.path += [SAMPLES_PATH]

'''
from duHast.Utilities.date_stamps import (
    get_date_stamped_file_name,
    get_file_date_stamp,
    get_folder_date_stamp,
)
'''


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
        ["test_get_date_stamped_file_name", test_get_date_stamped_file_name],
        ["test_get_folder_date_stamp", test_get_folder_date_stamp],
    ]

    # execute tests
    for test in tests:
        flag, message = test[1]()
        all_tests = all_tests & flag
        output(test[0], flag, message)

    return all_tests


if __name__ == "__main__":
    # in line function to print
    def action(function, flag, message):
        print("{} [{}]".format(function, flag))
        print(message)

    run_tests(action)
