import sys
SAMPLES_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'
sys.path += [SAMPLES_PATH]

import os
import shutil
import glob
import tempfile

from duHast.Utilities.files_get import get_files_from_directory_walker_with_filters, get_files_with_filter


def test_get_files_from_directory_walker_with_filters(tmpdir):
    flag = True
    try:
        # Create a temporary directory for testing
        test_dir = tmpdir.mkdir("test_dir")
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
            file_path = test_dir.join(file_name)
            file_path.write("test content")

        # Set up the input parameters for the function
        folder_path = str(test_dir)
        file_prefix = "prefix"
        file_suffix = "suffix"
        file_extension = ".csv"

        # Call the function to get the actual output
        actual_output = get_files_from_directory_walker_with_filters(
            folder_path, file_prefix, file_suffix, file_extension
        )

        # Check the actual output matches the expected output
        expected_output = [
            os.path.join(folder_path, "prefix_file5_suffix.csv"),
            os.path.join(folder_path, "prefix_file9_suffix.csv"),
        ]
        assert sorted(actual_output) == sorted(expected_output)

        # Remove the temporary directory and files
        shutil.rmtree(str(test_dir))
    except Excption as e:
        flag = False
        print ('An exception occurred in function test_get_files_from_directory_walker_with_filters {}'.format(e))
    return flag

def test_get_files_with_filter(tmpdir):
    
    flag = True
    try:
        # Create a temporary directory for testing
        test_dir = tmpdir.mkdir("test_dir")
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
            file_path = test_dir.join(file_name)
            file_path.write("test content")

        # Set up the input parameters for the function
        folder_path = str(test_dir)
        file_extension = ".rvt"
        filter = "something*"

        # Call the function to get the actual output
        actual_output = get_files_with_filter(folder_path, file_extension, filter)

        # Check the actual output matches the expected output
        expected_output = [
            os.path.join(folder_path, "something1.rvt"),
            os.path.join(folder_path, "something2.rvt"),
        ]
        assert sorted(actual_output) == sorted(expected_output)

        # Remove the temporary directory and files
        shutil.rmtree(str(test_dir))
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