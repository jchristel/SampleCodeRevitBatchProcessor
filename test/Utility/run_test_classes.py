"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module runs all revit revision related tests . 
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


from test.utils.run_tests import RunTest

# import test classes
from test.Utility import (
    get_date_stamp_directory,
    get_date_stamp_file,
    file_exist,
    file_delete,
    file_copy,
    file_rename,
    file_get_directory_path,
    file_name_without_extension,
    file_size,
    file_csv_read,
    file_csv_read_first_row,
    file_csv_write_report,
    util_encode_ascii,
    util_flatten_dictionary,
    util_get_first,
    util_get_index_of,
    util_pad_single_digit_string,
    util_remove_items,
    util_string_to_bool,
)


def run_tests():
    """
    Runs all utility related tests.

    :return: dictionary containing
         - the test name as key and as values
         - a flag (true if test completed successfully, otherwise false)
         - message string
    :rtype: {str:bool,str}
    """

    # list of tests to be run
    run_tests = [
        ["Encode ASCII", util_encode_ascii.EncodeASCII],
        ["Flatten Dictionary", util_flatten_dictionary.FlattenDictionary],
        ["Get First Item in List", util_get_first.GetFirst],
        ["Get Index Of Item In List", util_get_index_of],
        ["Pad Single Digit String", util_pad_single_digit_string],
        ["Remove Items From List", util_remove_items.RemoveItemsFromList],
        ["Parse String To Bool", util_string_to_bool.StringToBool],
        ["File Exist", file_exist.FileExist],
        ["File Delete", file_delete.FileDelete],
        ["File Copy", file_copy.FileCopy],
        ["File Rename", file_rename.FileRename],
        ["File Directory Path", file_get_directory_path.FileGetDirectory],
        [
            "File Name Without Extension",
            file_name_without_extension.FileNameWithoutExtension,
        ],
        ["File Size", file_size.FileSize],
        ["Directory Get Date Stamp", get_date_stamp_directory.GetDateStampDirectory],
        ["File Get Date Stamp", get_date_stamp_file.GetDateStampFile],
        ["Read CSV File", file_csv_read.FileCSVRead],
        ["Read CSV File First Row", file_csv_read_first_row.FileCSVReadFirstRow],
        ["Write CSF File Report", file_csv_write_report.FileCSVWriteReport],
    ]

    # run tests
    runner = RunTest(run_tests)
    return_value = runner.run_tests()

    return return_value
