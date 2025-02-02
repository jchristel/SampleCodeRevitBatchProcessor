"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to writing text files. 
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

from duHast.Utilities.files_io import (
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
    :param enforce_ascii: Flag to enforce ASCII encoding on data. If True, data will be encoded to ASCII. Defaults to False.
    :type enforce_ascii: bool, optional
    :param encoding: Encoding used to write the file. Defaults to 'utf-8'. None no encoding applied.
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

    # if no encoding is provided set the encoding to ascii (default)
    encoding_file_open = encoding if encoding is not None else "ascii"
    
    # Open the file with the codecs.open method to specify encoding
    with codecs.open(file_name, write_type, encoding=encoding_file_open) as f:
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

            # internal function to encode the row using the specified encoding
            def encoded_row(row):
                # Encode each string in the row using the specified encoding
                encoded = [s.encode(encoding).decode(encoding) for s in row]
                # check if also ascii encoding is enforced
                if enforce_ascii:
                    # enforce ascii encoding by removing non-ascii characters
                    return [
                        s.encode("ascii", "ignore").decode("ascii") for s in encoded
                    ]
                else:
                    # return the encoded row
                    return (
                        encoded  # Keep the strings in their current state for writing
                    )

            # Write header
            wrote_header = False
            if header and len(header) > 0:
                # check if encoding is required
                if encoding is not None:
                    # Encode the header using the specified encoding
                    header = encoded_row(header)
                writer.writerow(header)
                return_value.append_message(
                    "Header written to file. (including newline)"
                )
                # set flag that header was written
                wrote_header = True
            else:
                return_value.append_message("No header provided, skipping writing.")

            # Write data rows
            wrote_date = False
            if data and len(data) > 0:
                for i in range(len(data)):
                    row = data[i]
                    
                    # check if encoding is required
                    if encoding is not None:
                        # Encode the row using the specified encoding
                        row = encoded_row(data[i])
                    
                    # write the row data
                    # ( do not log what got written into results message property since that is a massive performance hit in the moment )
                    writer.writerow(row)
                    
                # set flag that data was written
                wrote_date = True
            else:
                return_value.append_message("No data provided, skipping writing.")

            # Remove the newline character from the last row if any data was written
            if wrote_date or wrote_header:
                f.flush()  # Ensure all data is written to the file
                with open(file_name, "rb+") as f:
                    f.seek(-1, 2)  # Move the cursor to the last character in the file
                    if f.read(1) == b"\n":
                        f.seek(-1, 2)  # Move the cursor back by one character
                        f.truncate()  # Truncate the file at the current cursor position
                        return_value.append_message(
                            "Removed newline character from the last row."
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
