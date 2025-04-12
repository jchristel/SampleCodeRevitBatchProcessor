"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions attempting to use .net library to read a text file whilst avoiding encoding errors. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

import clr
import os

from duHast.Utilities.Objects.result import Result

# load the wrapper dll from the libs folder
# the dll is located in the libs folder of the extension, which is one level up from the current file's directory
current_directory = os.path.dirname(__file__)
parent_directory = os.path.dirname(current_directory)
dll_path = os.path.join(parent_directory, "libs", "FileIOWrapper.dll")
clr.AddReference(dll_path)

# import the ReadFromFile class from the CSVHelperWrapper namespace
from duHastNet.FileIOWrapper import ReadFromColumnBasedTextFile, ReadFromTextFile

from duHast.Utilities.files_io import (
    get_file_name_without_ext,
)

def _read_text_file(file_path, delimiter=",", row_count=None):
    """
    Private helper function to read data from a text file using the CFileIOWrapper library.
    
    :param file_path: Path to the text file.
    :type file_path: str
    :param delimiter: Delimiter used in the text file. Default is ",".
    :type delimiter: str
    :param row_count: Number of rows to read. If None, reads the entire file.
    :type row_count: int or None
    
    :return:
        Result class instance.

        - result.status (bool) True if file was read without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will contain a list of nested lists of string representing the data read from the file.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
        - result.result will be an empty list.
    :rtype: :class:`.Result`
    """
    return_value = Result()
    
    try:
        # Validate input types
        if not isinstance(file_path, str):
            raise ValueError("file_path must be a string")
        if not isinstance(delimiter, str):
            raise ValueError("delimiter must be a string")
        if row_count is not None and not isinstance(row_count, int):
            raise ValueError("row_count must be an integer or None")
        
        # Instantiate the ReadFromFile class from the FileIO library
        reader_net = ReadFromColumnBasedTextFile()
        
        # Read the file based on row_count
        if row_count is None:
            result_list = reader_net.ReadFromTextFile(file_path, delimiter=delimiter)
        else:
            result_list = reader_net.ReadRowsFromTextFile(file_path, delimiter=delimiter, rowCount=row_count)
        
        # Handle empty result or errors
        if result_list.Count == 0:
            if reader_net.ErrorHistory.Count == 0:
                return_value.update_sep(True, "File was empty")
            else:
                for message in reader_net.ErrorHistory:
                    return_value.append_message(message)
                return_value.status = False
            return return_value
        
        # Convert .NET list to Python list
        for i in range(result_list.Count):
            nested_list = []
            for j in range(result_list[i].Count):
                nested_list.append(result_list[i][j])
            return_value.result.append(nested_list)
        
        return_value.update_sep(True, "Text file read from {} with status: {}".format(file_path, True))
        return return_value

    except Exception as e:
        return_value.update_sep(False, "Error reading text file: {}".format(e))
        return return_value


def read_from_delimited_text_file(file_path, delimiter=","):
    """
    Reads all data from a text file using the FileIOWrapper library.
    """
    return _read_text_file(file_path, delimiter)


def get_first_row_from_delimited_text_file(file_path, delimiter=","):
    """
    Reads the first row from a text file using the FileIOWrapper library.
    """
    return _read_text_file(file_path, delimiter, row_count=1)


def get_unique_headers(files, delimiter=","):
    """
    Gets a list of alphabetically sorted headers retrieved from text files.
    Assumes:

    - first row in each file is the header row

    :param files: List of file path from which the headers are to be returned.
    :type files: list of str
    :param delimiter: The delimiter used in the text file. Defaults to ','.
    :type delimiter: str, optional
    :return: List of headers.
    :rtype: list of str
    """

    headers_in_all_files = {}
    for f in files:
        
        # get unmodified row data and remove the next line character at the end
        data_result = get_first_row_from_delimited_text_file(f, delimiter=delimiter)
        if data_result.status is False:
            raise Exception("Failed to get headers from file: {}".format(f))

        # store the headers by file name
        headers_in_all_files[get_file_name_without_ext(f)] = data_result.result

    # create a list of unique headers
    headers_unique = []
    for header_by_file in headers_in_all_files:
        empty_header_counter = 0
        for header in headers_in_all_files[header_by_file]:
            # reformat any empty headers to be unique
            if header == "":
                header = header_by_file + ".Empty." + str(empty_header_counter)
                empty_header_counter = empty_header_counter + 1
            if header not in headers_unique:
                headers_unique.append(header)
    
    return sorted(headers_unique)


def read_non_delimited_text_file(file_path):
    """
    Read a non-column based text file.

    :param file_path: The fully qualified file path to the text file.
    :type file_path: str

    :return:
        Result class instance.

        - result.status (bool) True if file was read without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will contain the data read from file.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    
    try:
        # Validate input types
        if not isinstance(file_path, str):
            raise ValueError("file_path must be a string")
        
        # Instantiate the ReadFromFile class from the FileIO library
        reader_net = ReadFromTextFile()
        
        # Read the file
        result_list = reader_net.ReadNonColumnBasedTextFile(file_path)
        
        # Handle empty result or errors
        if result_list.Count == 0:
            if reader_net.ErrorHistory.Count == 0:
                return_value.update_sep(True, "File was empty")
            else:
                for message in reader_net.ErrorHistory:
                    return_value.append_message(message)
                return_value.status = False
            return return_value
        
        # Convert .NET list to Python list
        for i in range(result_list.Count):
            return_value.result.append(result_list[i])
            
        return_value.update_sep(True, "Text file read from {} with status: {}".format(file_path, True))
        return return_value

    except Exception as e:
        return_value.update_sep(
            False, "Failed to read file: {} with exception: {}".format(file_path, e)
        )
    
    return return_value