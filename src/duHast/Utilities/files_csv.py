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

#import clr
import codecs
import csv
import System.IO

from duHast.Utilities.files_io import get_file_name_without_ext, remove_null_bytes, file_delete
from duHast.Utilities.utility import encode_ascii
from duHast.Utilities.Objects.result import Result


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
        data = get_first_row_in_csv_file(f)
        headers_in_all_files[get_file_name_without_ext(f)] = data
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


def process_csv(file_path):
    """
    Process a CSV file by removing null bytes and then reading its content.

    :param file_path: The path to the CSV file to be processed.
    :type file_path: str
    """
    # Create a temporary file in the system's temp directory
    temp_file_path = System.IO.Path.GetTempFileName()
    
    row_list = []

    try:
        # Remove null bytes and save to a temporary file
        remove_null_bytes(file_path, temp_file_path)

        # Read the cleaned file with the CSV reader
        with open(temp_file_path, 'r') as cleaned_file:
            reader = csv.reader(cleaned_file)
            for row in reader:
                row_list.append(row)
            cleaned_file.close()
    finally:
        # Clean up the temporary file
        if System.IO.File.Exists(temp_file_path):
            System.IO.File.Delete(temp_file_path)
    
    return row_list


def read_csv_file_with_encoding(file_path_csv, increase_max_field_size_limit=False):
    """
    Read a csv file, attempting to detect and handle encoding, including BOMs.

    :param filepathCSV: The fully qualified file path to the csv file.
    :type filepathCSV: str
    :return: A list of list of strings representing the data in each row.
    :rtype: list of list of str
    """

    row_list = []
    encodings = ['utf-8-sig', 'utf-16']

    return_value = Result()
    if increase_max_field_size_limit:
        csv.field_size_limit(2147483647)

    for encoding in encodings:
        try:
            with codecs.open(file_path_csv, 'r', encoding=encoding) as csv_file:
                reader = csv.reader(csv_file)
                row_list = [row for row in reader]
            
            # Successful read
            return_value.append_message("read file succesfully")
            return_value.status=True
            return_value.result=row_list
            return return_value
        except (Exception) as e:
            return_value.update_sep(False, "Failed with encoding {}: {}".format(encoding, e))

    # statsu should be false 
    return_value.update_sep(False, "Failed to decode using known encodings.")
    return return_value


def read_csv_file(filepathCSV, increaseMaxFieldSizeLimit=False):
    """
    Read a csv file into a list of rows, where each row is another list.

    :param filepathCSV: The fully qualified file path to the csv file.
    :type filepathCSV: str
    :return: A list of list of strings representing the data in each row.
    :rtype: list of list of str
    """

    row_list = []
    # read with encoding enabled
    read_result = read_csv_file_with_encoding(filepathCSV, increaseMaxFieldSizeLimit)

    if read_result.status:
        return read_result.result
    
    # if that failed try the below...

    # hard coded hack
    if increaseMaxFieldSizeLimit:
        csv.field_size_limit(2147483647)

    try:
        with open(filepathCSV) as csv_file:
            reader = csv.reader(csv_file)
            row_list = [row for row in reader]
            csv_file.close()
    except csv.Error as e:
        # maybe a nullbyte exception?
        if "line contains NULL byte" in str(e):
            row_list = process_csv(filepathCSV)
        else:
            row_list = []
    except Exception as e:
        row_list = []
    return row_list


def get_first_row_in_csv_file(filePath):
    """
    Reads the first line of a csv text file and returns it as a list of strings
    :param filePath: The fully qualified file path.
    :type filePath: str
    :return: The first row of a text file.
    :rtype: str
    """

    return_value = []
    try:
        with open(filePath) as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:  # each row is a list
                return_value = row
                break
            csv_file.close()
    except Exception as e:
        print(str(e))
    return return_value


def write_report_data_as_csv(
    file_name, header, data, write_type="w", enforce_ascii=False,  encoding="utf-8", bom=None
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
    :param enforce_ascci: Flag to enforce ASCII encoding on data. If True, data will be encoded to ASCII. Defaults to False.
    :type enforce_ascci: bool, optional
    :param encoding: Encoding used to write the file. Defaults to 'utf-8'.
    :type encoding: str, optional
    :param bom: the byte order mark, Default is None (none will be written). BOM: "utf-16" = , "utf-16-le" = ,  utf-8 =
    :type bom: str, default is NoneType
    """

    # Open the file with the codecs.open method to specify encoding
    with codecs.open(file_name, write_type, encoding=encoding) as f:
        # Write BOM manually if specified
        if bom and 'w' in write_type:
            f.write(bom.decode(encoding))

        # Create the CSV writer
        writer = csv.writer(f)

        def encoded_row(row):
            if enforce_ascii:
                return [s.encode('ascii', 'ignore').decode('ascii') for s in row]
            else:
                return row  # Keep the strings in their current state for writing

        # Write header
        if header:
            writer.writerow(encoded_row(header))

        # Write data rows
        for row in data:
            writer.writerow(encoded_row(row))
                    
        f.close()

