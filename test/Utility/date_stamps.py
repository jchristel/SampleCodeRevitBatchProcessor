import os
from datetime import datetime


import sys
SAMPLES_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'
sys.path += [SAMPLES_PATH]

from duHast.Utilities.date_stamps import get_date_stamped_file_name, get_file_date_stamp, get_folder_date_stamp


def test_get_folder_date_stamp():
    '''
    _summary_

    :return: True if all tests pass, otherwise False
    :rtype: _bool
    '''

    flag = True
    message = '-'
    try:
        # Test with default format
        expected_result = datetime.now().strftime('%Y%m%d')
        result = get_folder_date_stamp()
        message = (' {} vs {}'.format(result, expected_result))
        assert result == expected_result

        # Test with a different format
        expected_result = datetime.now().strftime('%Y-%m-%d')
        result = get_folder_date_stamp('%Y-%m-%d')
        message = message + '\n' + (' {} vs {}'.format(result, expected_result))
        assert result == expected_result

        # Test with a invalid format
        expected_result = 'invalid-format'
        result = get_folder_date_stamp('invalid-format')
        message = message + '\n' + (' {} vs {}'.format(result, expected_result))
        assert result == expected_result
        
    except Exception as e:
        message = message + '\n' + ('An exception occurred in function test_get_file_name_without_ext {}'.format(e))
        flag = False
    return flag, message

def test_get_date_stamped_file_name():
    '''
    get_date_stamped_file_name() test

    :return: True if all tests pass, otherwise False
    :rtype: _bool
    '''

    flag = True
    message = '-'
    try:
        revit_file_path = 'C:/Users/User/Documents/RevitFile.rvt'
        file_extension = '.txt'
        file_suffix = '_backup'

        date_stamp = get_file_date_stamp()
        result = date_stamp + '_RevitFile_backup.txt'

        # Call the function to get the actual output
        expected_result = get_date_stamped_file_name(revit_file_path, file_extension, file_suffix)
        message = ' {} vs {}'.format(result, expected_result)
        
        # Assert the actual output matches the expected output
        assert  expected_result == result
    except Exception as e:
        print ('An exception occurred in function test_get_date_stamped_file_name {}'.format(e))
        flag = False
    return flag, message


def run_tests(output):
    '''
    Runs all tests in this module

    :param output: A function to direct any output to.
    :type output: fun(message)
    :return: True if all tests returned True, otherwise False
    :rtype: boolean
    '''

    all_tests = True

    flag, message = test_get_date_stamped_file_name()
    all_tests = all_tests & flag
    output('test_get_date_stamped_file_name()', flag, message)

    flag, message = test_get_folder_date_stamp()
    all_tests = all_tests & flag
    output('test_get_folder_date_stamp()', flag, message)

    return all_tests

if __name__ == "__main__":
    flag, message = test_get_date_stamped_file_name()
    print('test_get_date_stamped_file_name() [{}]'.format(flag))
    print(message)

    flag, message = test_get_folder_date_stamp()
    print('test_get_folder_date_stamp() [{}]'.format(flag))
    print(message)