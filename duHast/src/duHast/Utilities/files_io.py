"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to file IO operations. 
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

import os
import shutil

# from System.IO import Path


def file_exist(full_file_path):
    """
    Checks whether a file exists
    :param full_file_path: Fully qualified file path
    :type full_file_path: str
    :return: True file exists, otherwise False
    :rtype: bool
    """

    try:
        value = os.path.exists(full_file_path)
    except Exception:
        value = False
    return value


def file_delete(full_file_path):
    """
    Deletes file.

    :param full_file_path: Fully qualified file path
    :type full_file_path: str
    :return: True if deleted, otherwise False
    :rtype: bool
    """
    try:
        os.remove(full_file_path)
        value = True
    except Exception:
        value = False
    return value


def get_directory_path_from_file_path(file_path):
    """
    Extracts directory from file path.

    :param file_path: A fully qualified file path.
    :type file_path: str
    :return: If no exception occurs : A fully qualified directory path,else an empty string.
    :rtype: str
    """
    try:
        value = os.path.dirname(file_path)
    except Exception:
        value = ""
    return value


def rename_file(old_name, new_name):
    """
    Renames a file.
    :param old_name: Fully qualified file path to file to be renamed.
    :type old_name: str
    :param new_name: Fully qualified new file name.
    :type new_name: str
    :return: True file renamed, otherwise False
    :rtype: bool
    """

    try:
        os.rename(old_name, new_name)
        value = True
    except Exception:
        value = False
    return value


def copy_file(old_name, new_name):
    """
    Copies a file
    :param old_name: Fully qualified file path to file to be copied.
    :type old_name: str
    :param new_name: Fully qualified path to new file location and name.
    :type new_name: str
    :return: True file copied, otherwise False
    :rtype: bool
    """

    value = True
    try:
        shutil.copy(old_name, new_name)
    except Exception:
        value = False
    return value


#: file size in KB conversion
FILE_SIZE_IN_KB = 1024
#: file size in MB conversion
FILE_SIZE_IN_MB = 1024 * 1024
#: file size in GB conversion
FILE_SIZE_IN_GB = 1024 * 1024 * 1024


def get_file_size(file_path, unit=FILE_SIZE_IN_MB):
    """
    Get the file size in given units (default is MB)
    :param file_path: Fully qualified file path
    :type file_path: str
    :param unit: the file size unit, defaults to FILE_SIZE_IN_MB
    :type unit: int
    :return: The file size.
    :rtype: float
    """

    # default value if anything goes wrong
    size = -1
    try:
        size = os.path.getsize(file_path)
        # convert units
        size = size / unit
    except:
        pass
    return size


def convert_relative_path_to_full_path(relative_file_path, full_file_path):
    """
    removes '../..' or '../' from relative file path string and replaces it with full path derived path past in sample path.
    - relative path sample: 'C:/temp/../myfile.ext'
    - full file path sample: 'C:/temp/Sample/someOtherFile.ext'
    - returns: 'C:/temp/Sample/myfile.ext'
    :param relative_file_path: String containing relative file path annotation.
    :type relative_file_path: str
    :param full_file_path: A fully qualified file path of which the relative file path is a sub set.
    :type full_file_path: str
    :return: A fully qualified file path.
    :rtype: str
    """

    if r"..\.." in relative_file_path:
        two_up = os.path.abspath(os.path.join(full_file_path, r"..\.."))
        return two_up + relative_file_path[5:]
    elif ".." in relative_file_path:
        one_up = os.path.abspath(os.path.join(full_file_path, ".."))
        return one_up + relative_file_path[2:]
    else:
        return relative_file_path


def get_file_name_without_ext(file_path):
    """
    Returns the file name without the file extension.

    :param file_path: Fully qualified file path to file
    :type file_path: str
    :return: The file name.
    :rtype: str
    """

    file_name = os.path.basename(file_path)
    name_chunks = file_name.split(".")
    name = ""
    if len(name_chunks) > 1:
        name = ".".join(name_chunks[:-1])
    else:
        name = file_name
    return name


def get_file_extension(file_path):
    """
    Returns the file extension of give file name.

    :param file_path: The file name. Can be just the file name or also the fully qualified file path.
    :type file_path: str
    :return: The file extension in format '.extension'
    :rtype: str
    """

    # this will return a tuple of root and extension
    split_tup = os.path.splitext(file_path)
    # extract the file extension
    file_extension = split_tup[1]
    return file_extension


def read_text_file(file_path):
    """
    Reads a text file and returns its content as a single string.

    :param file_path: The fully qualified file path.
    :type file_path: str
    :return: The content of a text file.
    :rtype: str
    """

    file_content = None
    try:
        with open(file_path, "r") as file:
            file_content = file.read()
            file.close()
    except Exception:
        file_content = None
    return file_content


def read_text_file_into_list(file_path):
    """
    Reads a text file and returns its content as a list of string.

    It will return

    - one string per row
    - removed line break characters

    :param file_path: The fully qualified file path.
    :type file_path: str
    :return: The content of a text file. Can be an empty list if an exception occurred during file read.
    :rtype: [str]
    """

    lines = []
    file_content = read_text_file(file_path)
    if file_content != None:
        lines = file_content.splitlines()
    return lines


def get_first_row_in_file(file_path):
    """
    Reads the first line of a text file and returns it as a single string with any leading or trailing white spaces stripped!

    :param file_path: The fully qualified file path.
    :type file_path: str
    :return: The first row of a text file.
    :rtype: str
    """

    row = ""
    try:
        with open(file_path) as f:
            row = f.readline().strip()
    except Exception:
        row = None
    return row


def get_first_row_in_file_no_strip(file_path):
    """
    Reads the first line of a text file and returns it as a single string.

    Note this may contain a new line character at the end! ("\\n")

    :param file_path: The fully qualified file path.
    :type file_path: str
    :return: The first row of a text file.
    :rtype: str
    """

    row = ""
    try:
        with open(file_path) as f:
            row = f.readline()
    except Exception:
        row = None
    return row
