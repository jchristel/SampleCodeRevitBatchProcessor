"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to comma separated text files. 
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

import csv

from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_base_write import write_report_data
from duHast.Utilities.files_base_read import get_first_row_in_column_based_text_file, read_column_based_text_file

def get_unique_headers(files):
    """
    Gets a list of alphabetically sorted headers retrieved from text files.
    
    Assumes:

    - first row in each file is the header row
    - headers are separated by <tab> character

    :param files: List of file path from which the headers are to be returned.
    :type files: list of str
    
    :return: List of headers.
    :rtype: list of str
    """

    headers_in_all_files = {}
    for f in files:
        # get unmodified row data and remove the next line character at the end
        data = get_first_row_in_column_based_text_file(
            file_path=f,
            delimiter=","
        )
        
        header_row = []
        if data.status:
            header_row = data.result
        else:
            raise Exception("Failed to read header row from file: {}".format(f))
        
        headers_in_all_files[get_file_name_without_ext(f)] = header_row
        
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


def read_csv_file(filepathCSV, increaseMaxFieldSizeLimit=False):
    """
    Read a csv file into a list of rows, where each row is another list.

    :param filepathCSV: The fully qualified file path to the csv file.
    :type filepathCSV: str
    
    :return:
        Result class instance.

        - result.status (bool) True if file was read without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will contain a list of list of strings representing the data in each row.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # read with encoding enabled
    read_result = read_column_based_text_file(
        file_path=filepathCSV, 
        increase_max_field_size_limit=increaseMaxFieldSizeLimit,
        delimiter=','
    )
    
    return read_result


def get_first_row_in_csv_file(filePath):
    """
    Reads the first line of a csv text file and returns it as a list of strings
    :param filePath: The fully qualified file path.
    :type filePath: str
    :return:
        Result class instance.

        - result.status (bool) True if file was read without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will contain a list of list of strings representing the first row.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """
    
    return_value = Result()
    return_value = get_first_row_in_column_based_text_file(file_path=filePath, delimiter=',')
    return return_value
    


def write_report_data_as_csv(
    file_name, header, data, write_type="w", enforce_ascii=False,  encoding="utf-8", bom=None, quoting=csv.QUOTE_NONE, delimiter=','
):
    """
    Function writing out report information as CSV file.
    :param file_name: The reports fully qualified file path.
    :type file_name: str
    :param header: list of column headers
    :type header: list of str
    :param data: list of list of strings representing row data
    :type data: [[str,str,..]]
    :param write_type: Flag indicating whether existing report file is to be overwritten 'w' or appended to 'a', defaults to 'w'
    :type write_type: str, optional
    :param enforce_ascii: Flag to enforce ASCII encoding on data. If True, data will be encoded to ASCII. Defaults to False.
    :type enforce_ascii: bool, optional
    :param encoding: Encoding used to write the file. Defaults to 'utf-8'.
    :type encoding: str, optional
    :param bom: the byte order mark, Default is None (none will be written). BOM: "utf-16" = , "utf-16-le" = ,  utf-8 =
    :type bom: str, default is NoneType
    :param quoting: Quoting style used by the csv writer. Defaults to csv.QUOTE_NONE. Options are csv.QUOTE_ALL, csv.QUOTE_MINIMAL, csv.QUOTE_NONNUMERIC, csv.QUOTE_NONE
    :type quoting: int, optional
    
    :return:
        Result class instance.

        - result.status (bool) True if file was written without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    
    # use base function to write the data
    return_value = write_report_data (
        file_name=file_name, header=header, data=data, write_type=write_type, enforce_ascii=enforce_ascii,  encoding=encoding, bom=bom, quoting=quoting, delimiter=delimiter
    )
    
    return return_value
