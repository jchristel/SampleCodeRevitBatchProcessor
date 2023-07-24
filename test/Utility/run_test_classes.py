"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module runs all utility related tests . 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
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
    file_combine_files,
    file_combine_files_tab_independent_headers,
    file_combine_files_csv_independent_headers,
    file_append_files,
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
    file_json_write_data,
    file_json_read_data,
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
        ["Get Index Of Item In List", util_get_index_of.GetIndexOf],
        ["Pad Single Digit String", util_pad_single_digit_string.PadSingleDigitString],
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
        ["Combine files", file_combine_files.FileCombineFiles],
        [
            "Combine files tab varied headers",
            file_combine_files_tab_independent_headers.FileCombineFilesIndependentHeadersTab,
        ],
        [
            "Combine files csv varied headers",
            file_combine_files_csv_independent_headers.FileCombineFilesIndependentHeadersCSV,
        ],
        ["File append another file", file_append_files.FileAppendFile],
        ["Write JSON data to file", file_json_write_data.FileJSONWriteData],
        ["Read JSON data from file", file_json_read_data.FileJSONReadData],
    ]

    # run tests
    runner = RunTest(run_tests)
    return_value = runner.run_tests()

    return return_value
