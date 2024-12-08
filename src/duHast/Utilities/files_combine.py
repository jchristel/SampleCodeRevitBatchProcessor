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

import codecs
import glob
import os
import csv

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import get_file_name_without_ext
from duHast.Utilities.files_get import get_files_single_directory
from duHast.Utilities.files_tab import get_unique_headers as get_unique_headers_tab
from duHast.Utilities.files_tab import read_tab_separated_file, write_report_data
from duHast.Utilities.files_csv import get_unique_headers as get_unique_headers_csv
from duHast.Utilities.files_csv import read_csv_file, write_report_data_as_csv
from duHast.Utilities.files_json import read_json_data_from_file, write_json_to_file


def combine_files(
    folder_path,
    file_prefix="",
    file_suffix="",
    file_extension=".txt",
    output_file_name="result.txt",
    file_getter=get_files_single_directory,
    delimiter=",",
    quoting=csv.QUOTE_MINIMAL
):
    """
    Combines multiple text files into a single new file.
    Assumes:

    - files have a header row followed by data rows
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
    
    :return: A result object with status and message.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        # check a file getter function was provided
        if(file_getter is None):
            return_value.update_sep(False, "No file getter function provided.")
            return return_value
        # get files to combine using file getter function
        file_list = file_getter(folder_path, file_prefix, file_suffix, file_extension)
        
        # loop over file and combine...
        # newlines is set to '' to avoid double newlines on Windows
        result = open(os.path.join(folder_path, output_file_name), "w", newline='', encoding="utf-8")
        try:
            # lineterminator='\n' is set to avoid double newlines on Windows
            writer = csv.writer(result, delimiter=delimiter, quoting=quoting, lineterminator='\n')

            for file_index, file_ in enumerate(file_list):
                try:
                    line_counter = 0
                    with codecs.open(file_, "r", encoding="utf-8") as fp:
                        reader = csv.reader(fp, delimiter=delimiter)
                        lines = list(reader)
                        for i, line in enumerate(lines):
                            # ensure header from first file is copied over
                            if file_index == 0 and line_counter == 0 or line_counter != 0:
                                if file_index == len(file_list) - 1 and i == len(lines) - 1:
                                    # Write the last row of the last file without a newline character
                                    result.write(delimiter.join(line))
                                else:
                                    writer.writerow(line)
                            line_counter += 1

                    return_value.append_message("File: {} combined.".format(file_))
                except Exception as e:
                    return_value.update_sep(False, "File: {} failed to combine with exception: {}".format(file_, e))
        finally:
            # make sure to close the file
            result.close()
                    
    except Exception as e:
        return_value.update_sep(False, "Failed to combine files with exception: {}".format(e))
    return return_value

def append_to_file(source_file, append_file, ignore_first_row=False, delimiter=",", quoting=csv.QUOTE_MINIMAL):
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
    :return: A result object with status and message.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        # read file to append into memory...hopefully will never get in GB range in terms of file size
        with open(append_file, "r", encoding="utf-8") as fp:
            reader = csv.reader(fp, delimiter=delimiter)
            lines = list(reader)

        # newlines is set to '' to avoid double newlines on Windows
        with open(source_file, "a", encoding="utf-8", newline='') as f:
            # lineterminator='\n' is set to avoid double newlines on Windows
            writer = csv.writer(f, delimiter=delimiter, quoting=quoting, lineterminator='\n')
            if not ignore_first_row:
                # no need to add a newline character to the first row of the file
                # since this is writing entire rows to the file
                for line in lines:
                     # write entire new row to file
                    writer.writerow(line)
            else:
                # check if only a header row in file?
                if len(lines) > 1:
                    # check if we need to write a newline character into the file before writing any data
                    # if there is more than one row to be appended to the file and ignore_first_row is set
                    # this is to ensure that the first row is not appended to the last row of the file
                    if ignore_first_row and len(lines) == 2:
                        f.write('\n')
                    
                    # write the rest of the rows to the file
                    for i, line in enumerate(lines[1:]):
                        # check if we are at the last row to be appended to the file ( could also be the first and last row !)
                        if i == len(lines[1:]) - 1:
                            # Write the last row without a newline character at the end ( This requires a new line to be added to beginning of write!, see code above)
                            f.write(delimiter.join(line))
                        else:
                            # write entire new row to file
                            writer.writerow(line)

        return_value.append_message("File: {} appended to file: {}".format(append_file, source_file))
    except Exception as e:
        return_value.update_sep(False, "Failed to append file with exception: {}".format(e))
    return return_value


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
    output_file_name="result.txt",
    overwrite_existing=False,
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
    :param overwrite_existing: Will overwrite an existing output file if set to True, defaults to False ( append to existing output file)
    :type overwrite_existing: bool, optional
    """

    return_value = Result()
    try:
        file_list = glob.glob(
            folder_path + "\\" + file_prefix + "*" + file_suffix + file_extension
        )
        # build list of unique headers
        headers = get_unique_headers_tab(file_list)
        combined_file_name = os.path.join(folder_path, output_file_name)
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
                    # debug
                    return_value.result.append(padded_row)
                line_counter += 1
            
            # determine write type, default is append
            write_type = "a"
            # if overwrite existing is set, write type is write for the first file only!
            if(file_counter == 0 and overwrite_existing):
                write_type = "w"
            # write file data to combined file
            result_write = write_report_data(
                combined_file_name, 
                header=[], 
                data=lines_to_be_transferred, 
                write_type=write_type
            )
            # keep track of what happened
            return_value.update(result_write)
            file_counter += 1
        return_value.append_message("{} Files combined successfully.".format(file_counter))
    except Exception as e:
        return_value.update_sep(False, "Failed to combine files with exception: {}".format(e))
    return return_value

def combine_files_csv_header_independent(
    folder_path,
    file_prefix="",
    file_suffix="",
    file_extension=".txt",
    output_file_name="result.csv",
    overwrite_existing=False,
):
    """
    Used to combine report files into one file, files may have different number / named columns.

    Columns which are unique to some files will have as a value 'N/A' in files where those columns do not exist.
    File need to use <,> character as column separator. (.CSV)
    Assumes all files have a header row!

    :param folder_path: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folder_path: str
    :param file_prefix: Filter: File name starts with this value
    :type file_prefix: str
    :param file_suffix: Filter: File name ends with this value.
    :type file_suffix: str
    :param file_extension: Filter: File needs to have this file extension
    :type file_extension: str, format '.extension'
    :param output_file_name: The file name of the combined file, defaults to 'result.csv'
    :type output_file_name: str, optional
    :param overwrite_existing: Will overwrite an existing output file if set to True, defaults to False ( append to existing output file)
    :type overwrite_existing: bool, optional
    
    :return: A result object with status and message.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    
    try:
        file_list = glob.glob(
            folder_path + "\\" + file_prefix + "*" + file_suffix + file_extension
        )
        # build list of unique headers
        headers = get_unique_headers_csv(file_list)
        combined_file_name = os.path.join(folder_path, output_file_name)

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
                    # header row in first file...
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
                    # debug
                    return_value.result.append(padded_row)
                line_counter += 1
            
            # determine write type, default is append
            write_type = "a"
            # if overwrite existing is set, write type is write for the first file only!
            if(file_counter == 0 and overwrite_existing):
                write_type = "w"
            
            # write file data to combined file for each file read!
            result_write = write_report_data_as_csv(
                file_name=combined_file_name, 
                header=[], 
                data=lines_to_be_transferred, 
                write_type=write_type,
                enforce_ascii=False, 
                encoding="utf-8", 
                bom=None, 
                quoting=csv.QUOTE_MINIMAL
            )
            # keep track of what happened
            return_value.update(result_write)
            
            file_counter += 1
        return_value.append_message("{} Files combined successfully.".format(file_counter))
    except Exception as e:
        return_value.update_sep(False, "Failed to combine csv file with exception: {}".format(e))
    return return_value


def combine_files_json(
    folder_path,
    file_prefix="",
    file_suffix="",
    file_extension=".txt",
    output_file_name="result.txt",
    file_getter=get_files_single_directory,
):
    """
    Combines multiple json formatted text files into a single json list formatted file, where each file is a list entry.
    Assumes:

    - each file can contain a single line json formatted string

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

    # get all files to be combined
    file_list = file_getter(folder_path, file_prefix, file_suffix, file_extension)

    # read json data into a list of json objects
    json_objects = []
    for file in file_list:
        json_object = read_json_data_from_file(file_path=file)
        json_objects.append(json_object)

    # write json data out
    result_write = write_json_to_file(
        json_data=json_objects,
        data_output_file_path=os.path.join(folder_path, output_file_name),
    )

    # return flag only
    return result_write.status
