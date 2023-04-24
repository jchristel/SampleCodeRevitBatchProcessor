import os
from datetime import datetime
from pathlib import Path

import sys
SAMPLES_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'
sys.path += [SAMPLES_PATH]

from duHast.Utilities.date_stamps import get_date_stamped_file_name, get_file_date_stamp

def test_get_date_stamped_file_name():
    revit_file_path = 'C:/Users/User/Documents/RevitFile.rvt'
    file_extension = '.txt'
    file_suffix = '_backup'

    date_stamp = get_file_date_stamp()
    expected_output = date_stamp + '_RevitFile_backup.txt'

    # Call the function to get the actual output
    actual_output = get_date_stamped_file_name(revit_file_path, file_extension, file_suffix)

    print('actual: \n[{}] \nvs expected: \n[{}]'.format(actual_output,expected_output))
    # Assert the actual output matches the expected output
    assert actual_output == expected_output

if __name__ == "__main__":
    test_get_date_stamped_file_name()