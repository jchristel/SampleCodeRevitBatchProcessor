import os
from datetime import datetime
from pathlib import Path

import sys
SAMPLES_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'
sys.path += [SAMPLES_PATH]

from duHast.Utilities.date_stamps import get_date_stamped_file_name, get_file_date_stamp

def test_get_date_stamped_file_name():
    flag = True
    try:
        revit_file_path = 'C:/Users/User/Documents/RevitFile.rvt'
        file_extension = '.txt'
        file_suffix = '_backup'

        date_stamp = get_file_date_stamp()
        result = date_stamp + '_RevitFile_backup.txt'

        # Call the function to get the actual output
        expected_result = get_date_stamped_file_name(revit_file_path, file_extension, file_suffix)
        print(' {} vs {}'.format(result, expected_result))
        
        # Assert the actual output matches the expected output
        assert  expected_result == result
    except Exception as e:
        print ('An exception occurred in function test_get_date_stamped_file_name {}'.format(e))
        flag = False
    return flag


if __name__ == "__main__":
    flag = test_get_date_stamped_file_name()
    print('test_get_date_stamped_file_name() [{}]'.format(flag))