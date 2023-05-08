"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains revit views report test and clean function . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import sys, os
import clr

# require for ToList()
clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# add additional path
TEST_PATH = ""
SAMPLES_PATH = ""
# check if __file__ is defined. Not the case when running this in the revit python shell
# should work in batch processor!
try:
    # __file__ is defined
    TEST_PATH = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    )
    SAMPLES_PATH = os.path.join(TEST_PATH, r"duHast\src")
except:
    # __file__ is not defined, add manual path to repo. Not sure whether there is a better way...
    SAMPLES_PATH = (
        r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src"
    )
    TEST_PATH = r"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor"

sys.path += [SAMPLES_PATH, TEST_PATH]

from duHast.Utilities.files_csv import (
    read_csv_file,
)
from duHast.Utilities.directory_io import directory_delete, directory_exists
from duHast.Utilities.files_io import file_exist


def check_csv_file(test_file_path, expected_file_content,tmp_dir, calling_function_name ):
    
    flag = True
    message = "-"

    try:
        # double check...
        file_exist_status = file_exist(test_file_path)
        message = " file exists check: {}".format(file_exist_status)
        assert file_exist_status == True

        # read file content
        result_file_read = read_csv_file(test_file_path)
        expected_result_file_read = expected_file_content
        message = (
            message
            + "\n"
            + " file read results: \n {} \n vs \n {}".format(
                sorted(result_file_read), sorted(expected_result_file_read)
            )
        )
        assert sorted(result_file_read) == sorted(expected_result_file_read)

        # clean up...
        # remove the temp directory:
        del_temp_dir = directory_delete(tmp_dir)
        message = message + "\n" + " delete temp dir: {}".format(del_temp_dir)
        assert del_temp_dir == True
        temp_dir_exists = directory_exists(tmp_dir)
        message = message + "\n" + " deleted temp dir still exists: {}".format(temp_dir_exists)
        assert temp_dir_exists == False
    except Exception as e:
        message = (
            message
            + "\n"
            + ("An exception occurred in function {} {}".format(calling_function_name, e))
        )
        flag = False
    return flag, message