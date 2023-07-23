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
# Copyright © 2023, Jan Christel
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


import codecs
import glob
import os
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.files_get import get_files_single_directory
from duHast.Utilities.files_tab import get_unique_headers as get_unique_headers_tab
from duHast.Utilities.files_tab import read_tab_separated_file, write_report_data
from duHast.Utilities.files_csv import get_unique_headers as get_unique_headers_csv
from duHast.Utilities.files_csv import read_csv_file, write_report_data_as_csv


def combine_files(
    folder_path,
    file_prefix="",
    file_suffix="",
    file_extension=".txt",
    out_put_file_name="result.txt",
    file_getter=get_files_single_directory,
):
    """
    Combines multiple text files into a single new file.
    Assumes:

    - files have a header row followed by data rows
    - same number of headers (columns) in each files.
    - files have the same header names per column

    The new file will be saved into the same folder as the original files.

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
    :param file_getter: Function returning list of files to be combined, defaults to GetFilesSingleFolder
    :type file_getter: func(folder_path, file_prefix, file_suffix, file_extension), optional
    """

    file_list = file_getter(folder_path, file_prefix, file_suffix, file_extension)
    with open(folder_path + "\\" + out_put_file_name, "w") as result:
        file_counter = 0
        for file_ in file_list:
            line_counter = 0
            fp = open(file_, "r")
            lines = fp.readlines()
            fp.close()
            for line in lines:
                # ensure header from first file is copied over
                if file_counter == 0 and line_counter == 0 or line_counter != 0:
                    result.write(line)
                line_counter += 1

            file_counter += 1


def append_to_file(source_file, append_file, ignore_first_row=False):
    """
    Appends one text file to another. Assumes same number of headers (columns) in both files.

    :param source_file: The fully qualified file path of the file to which the other file will be appended.
    :type source_file: str
    :param append_file: The fully qualified file path of the file to be appended.
    :type append_file: str
    :param ignore_first_row: If True, first row of append file will not be appended to source file.
    :type ignore_first_row: bool
    :return: If True file was appended without an exception, otherwise False.
    :rtype: bool
    """

    flag = True
    try:
        # read file to append into memory...hopefully will never get in GB range in terms of file size
        fp = codecs.open(append_file, "r", encoding="utf-8")
        lines = fp.readlines()
        fp.close()
        with codecs.open(source_file, "a", encoding="utf-8") as f:
            if ignore_first_row == False:
                for line in lines:
                    f.write(line)
            else:
                # check if only a header row in file?
                if len(lines) > 1:
                    for x in range(1, len(lines)):
                        f.write(lines[x])
                        # get out to avoid out of index exception
                        # if I change the for loop to be
                        # for x in range(1, len(lines)-1):
                        # it will not process files with two rows only ( a header and a single data row! )
                        if x == len(lines) - 1:
                            break

    except Exception:
        flag = False
    return flag


def _format_headers(headers_in_file, file):
    """
    Replace any empty strings in header row

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
    out_put_file_name="result.txt",
):
    """
    Used to combine report files into one file, files may have different number / named columns.

    Columns which are unique to some files will have as a value 'N/A' in files where those columns do not exist.
    File need to use <tab> character as column separator

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
    """

    file_list = glob.glob(
        folder_path + "\\" + file_prefix + "*" + file_suffix + file_extension
    )
    # build list of unique headers
    headers = get_unique_headers_tab(file_list)
    combined_file_name = os.path.join(folder_path, out_put_file_name)
    # loop over files to be combined
    file_counter = 0
    for file in file_list:
        line_counter = 0
        column_mapper = []
        lines = read_tab_separated_file(file)
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
            line_counter += 1
        # write file data to combined file
        write_report_data(
            combined_file_name, header=[], data=lines_to_be_transferred, write_type="a"
        )
        file_counter += 1


def combine_files_csv_header_independent(
    folder_path,
    file_prefix="",
    file_suffix="",
    file_extension=".txt",
    out_put_file_name="result.csv",
):
    """
    Used to combine report files into one file, files may have different number / named columns.

    Columns which are unique to some files will have as a value 'N/A' in files where those columns do not exist.
    File need to use <,> character as column separator. (.CSV)

    :param folder_path: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folder_path: str
    :param file_prefix: Filter: File name starts with this value
    :type file_prefix: str
    :param file_suffix: Filter: File name ends with this value.
    :type file_suffix: str
    :param file_extension: Filter: File needs to have this file extension
    :type file_extension: str, format '.extension'
    :param out_put_file_name: The file name of the combined file, defaults to 'result.csv'
    :type out_put_file_name: str, optional
    """

    file_list = glob.glob(
        folder_path + "\\" + file_prefix + "*" + file_suffix + file_extension
    )
    # build list of unique headers
    headers = get_unique_headers_csv(file_list)
    combined_file_name = os.path.join(folder_path, out_put_file_name)

    # loop over files and combine...
    file_counter = 0
    for file in file_list:
        line_counter = 0
        column_mapper = []
        lines = read_csv_file(file, increaseMaxFieldSizeLimit=False)
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
                # map data columns to headers
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
            line_counter += 1
        # write file data to combined file
        write_report_data_as_csv(
            combined_file_name, header=[], data=lines_to_be_transferred, write_type="a"
        )
        file_counter += 1
