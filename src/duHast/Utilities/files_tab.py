"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to tab separated text files. 
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
from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_base_write import write_report_data
from duHast.Utilities.files_base_read import (
    get_first_row_in_column_based_text_file,
    read_column_based_text_file,
)
from duHast.Utilities.files_base_combine import (
    combine_files,
    combine_files_header_independent,
    append_to_file,
)
from duHast.Utilities.files_get import get_files_single_directory


def append_tab_separated_file(
    source_file, append_file, ignore_first_row=False, quoting=csv.QUOTE_MINIMAL
):
    """
    Function to append the content of a tab separated file to another tab separated file.

    :param source_file: The fully qualified file path of the source file.
    :type source_file: str
    :param append_file: The fully qualified file path of the file to append.
    :type append_file: str
    :param ignore_first_row: Flag to ignore the first row of the append file. Defaults to False.
    :type ignore_first_row: bool, optional
    :param quoting: Quoting style used by the csv writer. Defaults to csv.QUOTE_MINIMAL. Options are csv.QUOTE_ALL, csv.QUOTE_MINIMAL, csv.QUOTE_NONNUMERIC, csv.QUOTE_NONE
    :type quoting: int, optional

    :return:
        Result class instance.

        - result.status (bool) True if file was appended without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # use base function to append the file
    return_value = append_to_file(
        source_file=source_file,
        append_file=append_file,
        ignore_first_row=ignore_first_row,
        delimiter="\t",
        quoting=quoting,
    )

    return return_value


def combine_tab_separated_files_header_independent(
    folder_path,
    file_prefix="",
    file_suffix="",
    file_extension=".txt",
    output_file_name="result.txt",
    overwrite_existing=False,
):
    """
    Function to combine multiple tab separated files into a single tab separated file combining all headers.

    :param folder_path: The fully qualified folder path containing the tab separated files.
    :type folder_path: str
    :param file_prefix: The prefix of the tab separated files to be combined. Defaults to "".
    :type file_prefix: str, optional
    :param file_suffix: The suffix of the tab separated files to be combined. Defaults to "".
    :type file_suffix: str, optional
    :param file_extension: The extension of the tab separated files to be combined. Defaults to ".txt".
    :type file_extension: str, optional
    :param output_file_name: The name of the output file. Defaults to "result.txt".
    :type output_file_name: str, optional
    :param overwrite_existing: Flag to overwrite the existing output file. Defaults to False.
    :type overwrite_existing: bool, optional

    :return:
        Result class instance.

        - result.status (bool) True if files were combined without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an complete list of all rows appended.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # use base function to combine the files
    return_value = combine_files_header_independent(
        folder_path=folder_path,
        file_prefix=file_prefix,
        file_suffix=file_suffix,
        file_extension=file_extension,
        output_file_name=output_file_name,
        overwrite_existing=overwrite_existing,
        delimiter="\t",
    )

    return return_value


def combine_tab_separated_files(
    folder_path,
    file_prefix="",
    file_suffix="",
    file_extension=".txt",
    output_file_name="result.txt",
    file_getter=get_files_single_directory,
    quoting=csv.QUOTE_MINIMAL,
):
    """
    Function to combine multiple tab separated files into a single tab separated file.

    Assumes all files have the same header. (number of columns)

    :param folder_path: The fully qualified folder path containing the tab separated files.
    :type folder_path: str
    :param file_prefix: The prefix of the tab separated files to be combined. Defaults to "".
    :type file_prefix: str, optional
    :param file_suffix: The suffix of the tab separated files to be combined. Defaults to "".
    :type file_suffix: str, optional
    :param file_extension: The extension of the tab separated files to be combined. Defaults to ".txt".
    :type file_extension: str, optional
    :param output_file_name: The name of the output file. Defaults to "result.txt".
    :type output_file_name: str, optional
    :param file_getter: Function to get the files in the folder. Defaults to get_files_single_directory.
    :type file_getter: function, optional
    :param quoting: Quoting style used by the tab separated writer. Defaults to csv.QUOTE_MINIMAL. Options are csv.QUOTE_ALL, csv.QUOTE_MINIMAL, csv.QUOTE_NONNUMERIC, csv.QUOTE_NONE
    :type quoting: int, optional

    :return:
        Result class instance.

        - result.status (bool) True if files were combined without an exception, otherwise False.
        - result.message contains log messages.
        - result.result will be an empty list.

        On exception:

        - result.status (bool) will be False.
        - result.message will contain exception message.
    :rtype: :class:`.Result`
    """

    # use base function to combine the files
    return_value = combine_files(
        folder_path=folder_path,
        file_prefix=file_prefix,
        file_suffix=file_suffix,
        file_extension=file_extension,
        output_file_name=output_file_name,
        file_getter=file_getter,
        delimiter="\t",
        quoting=quoting,
    )

    return return_value


def write_report_data_as_tab_separated_file(
    file_name,
    header,
    data,
    write_type="w",
    enforce_ascii=False,
    encoding="utf-8",
    bom=None,
    quoting=csv.QUOTE_NONE,
):
    """
    Function writing out report information in tab separated format.

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

    :return: A Result object, with the result attribute set to True if the file was written successfully, False otherwise.
    :rtype: :class:`.Result`
    """

    write_result = write_report_data(
        file_name=file_name,
        header=header,
        data=data,
        write_type=write_type,
        enforce_ascii=enforce_ascii,
        encoding=encoding,
        quoting=quoting,
        bom=bom,
        delimiter="\t",
    )
    return write_result


def get_first_row_in_tab_separated_file(file_path):
    """
    Reads the first line of a tab separated text file and returns it as a list of strings

    :param file_path: The fully qualified file path.
    :type file_path: str
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
    return_value = get_first_row_in_column_based_text_file(
        file_path=file_path, delimiter="\t"
    )
    return return_value


def read_tab_separated_file(file_path, increase_max_field_size_limit=False):
    """
    Read a tab separated file into a list of rows, where each row is another list.

    :param file_path: The fully qualified file path to the tab separated text file.
    :type file_path: str
    :param increase_max_field_size_limit: Flag to increase the max field size limit. Defaults to False.
    :type increase_max_field_size_limit: bool, optional

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
        file_path=file_path,
        increase_max_field_size_limit=increase_max_field_size_limit,
        delimiter="\t",
    )

    return read_result
