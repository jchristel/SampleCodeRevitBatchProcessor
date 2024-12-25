"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to combining text files. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

import glob
import os
import csv

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.files_get import get_files_single_directory
from duHast.Utilities.files_base_read import (
    read_column_based_text_file as read_column_based_text_file_base,
)
from duHast.Utilities.files_base_read import (
    get_unique_headers as get_unique_headers_base,
)
from duHast.Utilities.files_base_write import (
    write_report_data as write_report_data_base,
)


def combine_files(
    folder_path,
    file_prefix="",
    file_suffix="",
    file_extension=".txt",
    output_file_name="result.txt",
    file_getter=get_files_single_directory,
    delimiter=",",
    quoting=csv.QUOTE_MINIMAL,
):
    """
    Combines multiple text files into a single new file.
    Assumes:

    - all files have a header row followed by data rows
    - same number of headers (columns) in each files.
    - files have the same header names per column
    - files are encoded in UTF-8!

    The new file will be saved into the same folder as the original files.

    :param folder_path: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folder_path: str
    :param file_prefix: Filter: File name starts with this value
    :type file_prefix: str
    :param file_suffix: Filter: File name ends with this value.
    :type file_suffix: str
    :param file_extension: Filter: File needs to have this file extension
    :type file_extension: str, format '.extension'
    :param output_file_name: The file name of the combined file, defaults to 'result.txt'
    :type output_file_name: str, optional
    :param file_getter: Function returning list of files to be combined, defaults to GetFilesSingleFolder
    :type file_getter: func(folder_path, file_prefix, file_suffix, file_extension), optional
    :param delimiter: The delimiter used in the files (e.g., ',' for CSV, '\t' for tab-separated), defaults to ','
    :type delimiter: str, optional
    :param quoting: The quoting option for the CSV writer, defaults to csv.QUOTE_MINIMAL
    :type quoting: int, optional

    :return:
        Result class instance.

        - result.status (bool) True if file content was combined without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        # check a file getter function was provided
        if file_getter is None:
            return_value.update_sep(False, "No file getter function provided.")
            return return_value

        # get files to combine using file getter function
        file_list = file_getter(folder_path, file_prefix, file_suffix, file_extension)

        # loop over file and combine...
        for file_index, file_ in enumerate(file_list):
            try:
                #line_counter = 0
                
                # attempt to read the file
                lines_result = read_column_based_text_file_base(file_, delimiter=delimiter)
                if lines_result.status is False:
                    return_value.update_sep(False, "Failed to read file: {} with {}".format(file_, lines_result.message))
                    # skip to next file
                    continue
                
                # get the lines read from the file
                lines = lines_result.result
                
                # determine write mode, default is append
                write_mode = "a"
                if file_index == 0:
                    write_mode = "w"
                    
                # determine if first row is header row and should be skipped in the write for any file other than the first
                if file_index != 0:
                    lines = lines[1:]
                
                write_result = write_report_data_base(
                    file_name=os.path.join(folder_path, output_file_name),
                    header=[],
                    data=lines,
                    write_type=write_mode,
                    delimiter=delimiter,
                    quoting=quoting
                )
                
                return_value.update(write_result)
            except Exception as e:
                return_value.update_sep(False, "File: {} failed to combine with exception: {}".format(file_, e))
        
    except Exception as e:
        return_value.update_sep(
            False, "Failed to combine files with exception: {}".format(e)
        )
    return return_value


def _format_headers(headers_in_file, file):
    """
    Replace any empty strings in header row with unique values based on the file name and a counter.

    :param headers_in_file: list of header entries
    :type headers_in_file: [str]
    :param file: Fully qualified file name
    :type file: str

    :return: Header row
    :rtype:[str]
    """

    file_name = get_file_name_without_ext(file)
    empty_header_counter = 0
    for i in range(len(headers_in_file)):
        # reformat any empty headers to be unique
        if headers_in_file[i] == "":
            headers_in_file[i] = file_name + ".Empty." + str(empty_header_counter)
            empty_header_counter = empty_header_counter + 1
    return headers_in_file


def combine_files_header_independent(
    folder_path,
    file_prefix="",
    file_suffix="",
    file_extension=".txt",
    output_file_name="result.txt",
    overwrite_existing=False,
    delimiter=",",
):
    """
    Used to combine report files into one file, files may have different number / named columns.

    Columns which are unique to some files will have as a value 'N/A' in files where those columns do not exist.

    :param folder_path: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folder_path: str
    :param file_prefix: Filter: File name starts with this value
    :type file_prefix: str
    :param file_suffix: Filter: File name ends with this value.
    :type file_suffix: str
    :param file_extension: Filter: File needs to have this file extension
    :type file_extension: str, format '.extension'
    :param out_put_file_name: The file name of the combined file, defaults to 'result.txt'
    :type out_put_file_name: str, optional
    :param overwrite_existing: Will overwrite an existing output file if set to True, defaults to False ( append to existing output file)
    :type overwrite_existing: bool, optional
    :param delimiter: The delimiter used in the files (e.g., ',' for CSV, '\t' for tab-separated), defaults to ','
    :type delimiter: str, optional

    :return:
        Result class instance.

        - result.status (bool) True if file content was combined without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be complete list of rows appended.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        file_list = glob.glob(
            folder_path + "\\" + file_prefix + "*" + file_suffix + file_extension
        )

        # build list of unique headers
        headers = get_unique_headers_base(file_list, delimiter)
        combined_file_name = os.path.join(folder_path, output_file_name)

        # loop over files to be combined
        file_counter = 0
        for file in file_list:
            line_counter = 0
            column_mapper = []

            lines_result = read_column_based_text_file_base(
                file_path=file, delimiter=delimiter
            )
            if lines_result.status is False:
                raise Exception(
                    "Failed to read file: {} with {}".format(file, lines_result.message)
                )

            # get the lines read from the file
            lines = lines_result.result

            lines_to_be_transferred = []
            for line in lines:
                # read the headers in file
                if line_counter == 0:
                    # replace any empty strings in header
                    headers_in_file = _format_headers(line, file)
                    # match up unique headers with headers from this file
                    # build header mapping
                    for unique_header in headers:
                        if unique_header in headers_in_file:
                            column_mapper.append(headers_in_file.index(unique_header))
                        else:
                            column_mapper.append(-1)

                # ensure unique header is written to file
                if file_counter == 0 and line_counter == 0:
                    lines_to_be_transferred.append(headers)
                elif line_counter != 0:
                    padded_row = []
                    for cm in column_mapper:
                        if cm == -1:
                            # this column does not exist in this file
                            padded_row.append("N/A")
                        elif cm > len(line):
                            # less columns in file than mapper index (should'nt happen??)
                            padded_row.append("index out of bounds")
                        else:
                            padded_row.append(line[cm])
                    lines_to_be_transferred.append(padded_row)
                    # debug
                    return_value.result.append(padded_row)
                line_counter += 1

            # determine write type, default is append
            write_type = "a"
            # if overwrite existing is set, write type is write for the first file only!
            if file_counter == 0 and overwrite_existing:
                write_type = "w"
            # write file data to combined file
            result_write = write_report_data_base(
                combined_file_name,
                header=[],
                data=lines_to_be_transferred,
                write_type=write_type,
                delimiter=delimiter,
            )
            # keep track of what happened
            return_value.update(result_write)
            file_counter += 1
        return_value.append_message(
            "{} Files combined successfully.".format(file_counter)
        )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to combine files with exception: {}".format(e)
        )
    return return_value


def append_to_file(
    source_file,
    append_file,
    ignore_first_row=False,
    delimiter=",",
    quoting=csv.QUOTE_MINIMAL,
):
    """
    Appends one text file to another.

    Assumes:

        - same number of headers (columns) in both files.
        - files are encoded in UTF-8!

    :param source_file: The fully qualified file path of the file to which the other file will be appended.
    :type source_file: str
    :param append_file: The fully qualified file path of the file to be appended.
    :type append_file: str
    :param ignore_first_row: If True, first row of append file will not be appended to source file.( Assumed its a header row )
    :type ignore_first_row: bool
    :param delimiter: The delimiter used in the files (e.g., ',' for CSV, '\t' for tab-separated), defaults to ','
    :type delimiter: str, optional
    :param quoting: The quoting option for the CSV writer, defaults to csv.QUOTE_MINIMAL
    :type quoting: int, optional

    :return:
        Result class instance.

        - result.status (bool) True if file content was appended without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()
        
    try:
        # read file to append into memory...hopefully will never get in GB range in terms of file size
        lines_result = read_column_based_text_file_base(
            append_file, delimiter=delimiter
        )
        if lines_result.status is False:
            return_value.update_sep(
                False,
                "Failed to read file: {} with {}".format(
                    append_file, lines_result.message
                ),
            )
            return return_value

        # get the lines read from the file depending on whether the first row is to be ignored
        lines = []
        if ignore_first_row:
            # remove the first row from the lines to be appended
            lines = lines_result.result[1:]
        else:
            # get the lines from the file
            lines = lines_result.result
        
        # write data to file
        write_result = write_report_data_base(
            file_name=source_file,
            header=[],
            data=lines,
            write_type="a",
            delimiter=delimiter,
            quoting=quoting,
        )

        return_value.update(write_result)
        
    except Exception as e:
        return_value.update_sep(
            False, "Failed to append file with exception: {}".format(e)
        )
    return return_value
