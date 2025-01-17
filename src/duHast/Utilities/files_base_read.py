"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to reading text files. 
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

import codecs
import csv
import System.IO

from duHast.Utilities.files_io import (
    remove_null_bytes,
    file_delete,
    file_exist,
    get_file_name_without_ext,
)

from duHast.Utilities.Objects.result import Result


def read_column_based_text_file_without_encoding(
    file_path, increase_max_field_size_limit=False, delimiter=","
):
    """
    Read a column based text file, without any encoding.

    :param file_path: The fully qualified file path to the csv file.
    :type file_path: str
    :param increase_max_field_size_limit: Flag to increase the max field size limit. Defaults to False.
    :type increase_max_field_size_limit: bool, optional
    :param delimiter: The delimiter used in the text file. Defaults to ','.
    :type delimiter: str, optional

    :return:
        Result class instance.

        - result.status (bool) True if file content was read without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will contain a list of list of strings representing the data in each row.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()

    # Initialize the row list
    row_list = []

    # check if the max field size limit should be increased
    if increase_max_field_size_limit:
        csv.field_size_limit(2147483647)

    # attempt to read the file
    try:
        with open(file_path) as csv_file:
            try:
                reader = csv.reader(csv_file, delimiter=delimiter)
                row_list = [row for row in reader]
                return_value.update_sep(
                    True, "Read file: {} successfully.".format(file_path)
                )
            except Exception as e:
                return_value.update_sep(
                    False,
                    "Failed to read file: {} with exception: {}".format(file_path, e),
                )
            finally:
                csv_file.close()
    except Exception as e:
        return_value.update_sep(
            False, "Failed to read file: {} with exception: {}".format(file_path, e)
        )

    return_value.result = row_list
    return return_value


def read_column_based_text_file_with_encoding(
    file_path, increase_max_field_size_limit=False, delimiter=","
):
    """
    Read a column based text file, attempting to detect and handle encoding, including BOMs.

    :param file_path: The fully qualified file path to the csv file.
    :type file_path: str
    :param increase_max_field_size_limit: Flag to increase the max field size limit. Defaults to False.
    :type increase_max_field_size_limit: bool, optional
    :param delimiter: The delimiter used in the text file. Defaults to ','.
    :type delimiter: str, optional

    :return:
        Result class instance.

        - result.status (bool) True if file content was read without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will contain a list of list of strings representing the data in each row.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()

    # Initialize the row list
    row_list = []

    # Define the encodings to try
    encodings = ["utf-8-sig", "utf-16"]

    # check if the max field size limit should be increased
    if increase_max_field_size_limit:
        csv.field_size_limit(2147483647)

    for encoding in encodings:
        try:
            with codecs.open(file_path, "r", encoding=encoding) as txt_file:
                try:
                    reader = csv.reader(txt_file, delimiter=delimiter)
                    row_list = list(reader)
                    # Successful read
                    return_value.update_sep(
                        True,
                        "Read file: {} successfully with encoding: {} and delimiter: [{}]".format(
                            file_path, encoding, delimiter
                        ),
                    )
                    return_value.result = row_list
                    # back to caller
                    return return_value
                except Exception as e:
                    return_value.update_sep(
                        False,
                        "Failed to read file: {} with exception: {}".format(
                            file_path, e
                        ),
                    )
                finally:
                    txt_file.close()
        except Exception as e:
            return_value.update_sep(
                False,
                "Failed to read file: {} with encoding {}: {}".format(
                    file_path, encoding, e
                ),
            )

    # status should be false
    return_value.append_message("Failed to decode using all known encodings.")
    return return_value


def process_txt_file(file_path, delimiter=","):
    """
    Process a txt file by removing null bytes and then reading its content without encoding.

    :param file_path: The path to the CSV file to be processed.
    :type file_path: str
    :param delimiter: The delimiter used in the text file. Defaults to ','.
    :type delimiter: str, optional

    :return:
        Result class instance.

        - result.status (bool) True if file content was read without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will contain a list of list of strings representing the data in each row.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    # Create a temporary file in the system's temp directory
    temp_file_path = System.IO.Path.GetTempFileName()

    try:
        return_value.append_message(
            "Attempting to remove any null bytes from txt file: {}".format(file_path)
        )

        # Remove null bytes and save to a temporary file
        remove_null_bytes(file_path, temp_file_path)

        return_value.append_message(
            "Removed any existing null bytes from txt file: {}".format(file_path)
        )

        # Read the cleaned file with the CSV reader without encoding
        file_reader_status = read_column_based_text_file_without_encoding(
            file_path=temp_file_path,
            increase_max_field_size_limit=False,
            delimiter=delimiter,
        )

        # get log messages
        return_value.update_sep(file_reader_status.status, file_reader_status.message)

        # get the row list
        return_value.result = file_reader_status.result

    except Exception as e:
        return_value.update_sep(
            False, "Failed to clean txt file with exception: {}".format(e)
        )
    finally:
        # Clean up the temporary file
        if file_exist(temp_file_path):
            file_delete(temp_file_path)
    return return_value


def read_column_based_text_file(
    file_path, increase_max_field_size_limit=False, delimiter=","
):
    """
    Read a csv file into a list of rows, where each row is another list.

    Attempts to read the file with encoding first, then without encoding if that fails. Encoding is attempted first because it is more likely to be successful.
    The following encodings are attempted: 'utf-8-sig', 'utf-16'.

    :param file_path: The fully qualified file path to the csv file.
    :type file_path: str
    :param increase_max_field_size_limit: Flag to increase the max field size limit. Defaults to False.
    :type increase_max_field_size_limit: bool, optional
    :param delimiter: The delimiter used in the text file. Defaults to ','.
    :type delimiter: str, optional

    :return:
        Result class instance.

        - result.status (bool) True if file content was read without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will contain a list of list of strings representing the data in each row.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()

    # read with encoding enabled first
    read_result = read_column_based_text_file_with_encoding(
        file_path=file_path,
        increase_max_field_size_limit=increase_max_field_size_limit,
        delimiter=delimiter,
    )

    # if reading with encoding worked return the result
    if read_result.status:
        return read_result

    # if that failed try the below...
    # try to read file without encoding
    try:
        # Read the cleaned file with the CSV reader without encoding
        file_reader_status = read_column_based_text_file_without_encoding(
            file_path=file_path,
            increase_max_field_size_limit=increase_max_field_size_limit,
            delimiter=delimiter,
        )

        # if reading without encoding worked return the result
        if file_reader_status.status:
            return file_reader_status

        # get log messages
        return_value.update_sep(file_reader_status.status, file_reader_status.message)

        # check for null byte exception
        if "line contains NULL byte" in file_reader_status.message:
            # attempt to remove null byte exception
            cleaned_rows_result = process_txt_file(file_path, delimiter)

            # if reading after cleaning and without encoding worked return the result
            if cleaned_rows_result.status:
                return cleaned_rows_result

            # get log messages
            return_value.update_sep(
                cleaned_rows_result.status, cleaned_rows_result.message
            )

    except Exception as e:
        return_value.update_sep(
            False, "Failed to read txt file with exception: {}".format(e)
        )

    # this is only executed if all attempts failed
    return return_value


def get_first_row_in_column_based_text_file(file_path, delimiter=","):
    """
    Reads the first line of a column based text file and returns it as a list of strings.

    :param file_path: The fully qualified file path.
    :type file_path: str
    :param delimiter: The delimiter used in the text file. Defaults to ','.
    :type delimiter: str, optional
    :param encoding: Encoding used to read the file. Defaults to 'utf-8'.
    :type encoding: str, optional

    :return:
        Result class instance.

        - result.status (bool) True if file content was read without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will contain a list of list of strings representing the first row.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    return_value = Result()

    # try to read the file
    return_value_read_file = read_column_based_text_file(
        file_path=file_path, increase_max_field_size_limit=False, delimiter=delimiter
    )

    # if read was successful, return the first row
    if return_value_read_file.status:
        # check how many rows were read
        if len(return_value_read_file.result) > 0:
            # return the first row
            return_value.result = return_value_read_file.result[0]
            return_value.append_message(
                "First row read from file: {}".format(file_path)
            )
        else:
            # no data found in file
            return_value.update_sep(
                False, "No data found in file: {}".format(file_path)
            )

    return return_value


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
        data_result = get_first_row_in_column_based_text_file(f, delimiter=delimiter)
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

def read_non_column_based_text_file(file_path):
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

    file = None
    try:
        # Read the data from the file
        with open(file_path, "r") as file:
            content = file.read()
            return_value.result = content
            return_value.update_sep(
                True, "Read file: {} successfully.".format(file_path)
            )

    except Exception as e:
        return_value.update_sep(
            False, "Failed to read file: {} with exception: {}".format(file_path, e)
        )

    finally:
        if file is not None:
            file.close()

    return return_value