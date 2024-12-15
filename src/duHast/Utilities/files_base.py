"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to text files. 
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
    is_last_char_newline,
)

from duHast.Utilities.Objects.result import Result


def write_report_data(
    file_name,
    header,
    data,
    write_type="w",
    enforce_ascii=False,
    encoding="utf-8",
    bom=None,
    quoting=csv.QUOTE_NONE,
    delimiter=",",
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
    :param quoting: Quoting style used by the csv writer. Defaults to csv.QUOTE_NONE. Options are csv.QUOTE_ALL, csv.QUOTE_MINIMAL, csv.QUOTE_NONNUMERIC, csv.QUOTE_NONE
    :type quoting: int, optional

    :return: A Result object, with the result attribute set to True if the file was written successfully, False otherwise.
    :rtype: :class:`.Result`
    """

    return_value = Result()

    # set a flag to check if we need to add a newline before writing
    need_newline = False
    # if in append mode, check if the last character is a newline
    if write_type == "a":
        if not is_last_char_newline(file_name):
            # if not, we need to add a newline before writing
            need_newline = True
            return_value.append_message(
                "File: {} is in append mode, but last character is not a newline.".format(
                    file_name
                )
            )

    # Open the file with the codecs.open method to specify encoding
    with codecs.open(file_name, write_type, encoding=encoding) as f:
        try:
            # Write a newline character if appending to the file to make sure we are starting on a new line
            if write_type == "a" and need_newline:
                f.write("\n")

            # Write BOM manually if specified
            if bom and "w" in write_type:
                f.write(bom.decode(encoding))

            # Create the CSV writer
            # line terminator is set to '\n' to avoid double newlines on Windows
            writer = csv.writer(
                f,
                delimiter=delimiter,
                escapechar="\\",
                quoting=quoting,
                lineterminator="\n",
            )

            def encoded_row(row):
                if enforce_ascii:
                    return [s.encode("ascii", "ignore").decode("ascii") for s in row]
                else:
                    return row  # Keep the strings in their current state for writing

            # Write header
            if header:
                # check if header only or if there is data to write as well
                if data:
                    # Write the header row with the CSV writer including a new line character
                    writer.writerow(encoded_row(header))
                    return_value.append_message(
                        "Header written to file. (including newline)"
                    )
                else:
                    # Write the header row without a newline character
                    f.write(delimiter.join(encoded_row(header)))
                    return_value.append_message(
                        "Header written to file. (including newline)"
                    )
            else:
                return_value.append_message("No header provided to write to file.")

            # Write data rows, looping over rows to prevent new line character on the last row
            for i in range(len(data)):
                row = data[i]
                if i == len(data) - 1:
                    # Write the last row without a newline character
                    f.write(delimiter.join(encoded_row(row)))
                    return_value.append_message(
                        "Last row {} written to file. (without newline)>>{}".format(
                            ",".join(encoded_row(row)), i
                        )
                    )
                else:
                    writer.writerow(encoded_row(row))
                    return_value.append_message(
                        "Row {} written to file. (including newline)>>{}".format(
                            ",".join(encoded_row(row)), i
                        )
                    )

        except Exception as e:
            return_value.update_sep(
                False,
                "File: {} failed to write data with exception: {}".format(file_name, e),
            )
        finally:
            # make sure to close the file
            f.close()

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

    :return: A Result object, with the result attribute set to a list of list of strings representing the data in each row.
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
                    return_value.update_sep(True, "Read file successfully")
                    return_value.result = row_list
                    # back to caller
                    return return_value
                except Exception as e:
                    return_value.update_sep(
                        False, "Failed to read txt file with exception: {}".format(e)
                    )
                finally:
                    txt_file.close()
        except Exception as e:
            return_value.update_sep(
                False, "Failed with encoding {}: {}".format(encoding, e)
            )

    # status should be false
    return_value.append_message("Failed to decode using all known encodings.")
    return return_value


def process_txt_file(file_path, delimiter=","):
    """
    Process a txt file by removing null bytes and then reading its content.

    :param file_path: The path to the CSV file to be processed.
    :type file_path: str
    :param delimiter: The delimiter used in the text file. Defaults to ','.
    :type delimiter: str, optional

    :return: A Result object, with the result attribute set to a list of list of strings representing the data in each row.
    :rtype: :class:`.Result
    """

    return_value = Result()
    # Create a temporary file in the system's temp directory
    temp_file_path = System.IO.Path.GetTempFileName()

    row_list = []

    try:
        # Remove null bytes and save to a temporary file
        remove_null_bytes(file_path, temp_file_path)

        # Read the cleaned file with the CSV reader
        with open(temp_file_path, "r") as cleaned_file:
            reader = csv.reader(cleaned_file, delimiter=delimiter)
            row_list = [row for row in reader]
            return_value.result = row_list
            cleaned_file.close()
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

    :return: A Result object, with the result attribute set to a list of list of strings representing the data in each row.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    # Initialize the row list
    row_list = []

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

    # hard coded hack
    if increase_max_field_size_limit:
        csv.field_size_limit(2147483647)

    # try to read file without encoding
    try:
        with open(file_path) as csv_file:
            try:
                reader = csv.reader(csv_file, delimiter=delimiter)
                row_list = [row for row in reader]
                return_value.update_sep(
                    True, "Read file {} successfully.".format(file_path)
                )
            except Exception as e:
                return_value.update_sep(
                    False,
                    "Failed to read txt file {} with exception: {}".format(
                        file_path, e
                    ),
                )
            finally:
                csv_file.close()
    except csv.Error as e:
        # maybe a null byte exception?
        if "line contains NULL byte" in str(e):
            # attempt to remove null byte exception
            cleaned_rows_result = process_txt_file(file_path, delimiter)
            if cleaned_rows_result.status:
                row_list = cleaned_rows_result.result
            else:
                row_list = []
        else:
            row_list = []
    except Exception as e:
        return_value.update_sep(
            False, "Failed to read txt file with exception: {}".format(e)
        )

    return_value.result = row_list
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

    :return: A Result object, with the first row of a text file in its result attribute.
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
