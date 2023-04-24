import sys
SAMPLES_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'
sys.path += [SAMPLES_PATH]

import os
import shutil
import glob
import tempfile

from duHast.Utilities.files_get import get_files_from_directory_walker_with_filters, get_files_with_filter


def test_get_files_from_directory_walker_with_filters(tmpdir):
    '''
    get_files_from_directory_walker_with_filters test

    :param tmpdir: temp directory
    :type tmpdir: str
    :return: True if all tests past, otherwise False
    :rtype: _bool
    '''
    
    flag = True
    try:
        # Create some files with different prefixes, suffixes, and extensions
        test_files = [
            "file1_prefix_suffix.csv",
            "file2_prefix_suffix.txt",
            "prefix_file3_suffix.jpg",
            "file4_prefix_suffix.png",
            "prefix_file5_suffix.csv",
            "prefix_file6_suffix.txt",
            "file7_prefix_suffix.jpg",
            "file8_prefix_suffix.txt",
            "prefix_file9_suffix.csv",
            "file10_prefix_suffix.jpg",
        ]
        for file_name in test_files:
            file_path = os.path.join(tmp_dir, file_name)
            with open(file_path, "w") as f1:
                f1.write("test content")

        # Set up the input parameters for the function
        folder_path = tmpdir
        file_prefix = "prefix"
        file_suffix = "suffix"
        file_extension = ".csv"

        # Call the function to get the actual output
        result = get_files_from_directory_walker_with_filters(
            folder_path, file_prefix, file_suffix, file_extension
        )

        # Check the actual output matches the expected output
        expected_result = [
            os.path.join(folder_path, "prefix_file5_suffix.csv"),
            os.path.join(folder_path, "prefix_file9_suffix.csv"),
        ]

        assert sorted(result) == sorted(expected_result)

    except Exception as e:
        flag = False
        print ('An exception occurred in function test_get_files_from_directory_walker_with_filters {}'.format(e))
    return flag

def test_get_files_with_filter(tmpdir):
    '''
    get_files_with_filter test

    :param tmpdir: temp directory
    :type tmpdir: str
    :return: True if all tests past, otherwise False
    :rtype: _bool
    '''

    flag = True
    try:
        # Create some files with different extensions and names
        test_files = [
            "file1.rvt",
            "file2.rvt",
            "file3.rfa",
            "file4.rvt",
            "something1.rvt",
            "something2.rvt",
            "nothing.txt",
        ]

        for file_name in test_files:
            file_path = os.path.join(tmp_dir, file_name)
            with open(file_path, "w") as f1:
                f1.write("test content")

        # Set up the input parameters for the function
        folder_path = tmpdir
        file_extension = ".rvt"
        filter = "something*"

        # Call the function to get the actual output
        result = get_files_with_filter(folder_path, file_extension, filter)

        # Check the actual output matches the expected output
        expected_result = [
            os.path.join(folder_path, "something1.rvt"),
            os.path.join(folder_path, "something2.rvt"),
        ]
        
        assert sorted(result) == sorted(expected_result)
       
    except Exception as e:
        flag = False
        print ('An exception occurred in function test_get_files_with_filter {}'.format(e))
    return flag

if __name__ == "__main__":

    # set up a temp directory, this should be os independent
    with tempfile.TemporaryDirectory() as tmp_dir:
        flag = test_get_files_with_filter(tmp_dir)
        print('test_get_files_with_filter [{}]'.format(flag))
        flag = test_get_files_from_directory_walker_with_filters(tmp_dir)
        print('test_get_files_from_directory_walker_with_filters [{}]'.format(flag))