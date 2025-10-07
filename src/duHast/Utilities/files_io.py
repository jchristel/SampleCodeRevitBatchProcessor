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

import os
import shutil
import re
import time

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
        value = os.path.isfile(full_file_path)
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


def files_delete_in_directory(directory_path, file_pattern="*.*"):
    """
    Deletes all files in a directory matching the given file pattern.

    :param directory_path: Fully qualified directory path
    :type directory_path: str
    :param file_pattern: File pattern to match, defaults to "*.*"
    :type file_pattern: str
    :return: True if all files deleted, otherwise False
    :rtype: bool
    """
    value = True
    try:
        # Convert the file pattern to a regex pattern
        regex_pattern = re.compile(fnmatch.translate(file_pattern))
        for file_name in os.listdir(directory_path):
            if regex_pattern.match(file_name):
                full_file_path = os.path.join(directory_path, file_name)
                if os.path.isfile(full_file_path):
                    try:
                        os.remove(full_file_path)
                    except Exception:
                        continue
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


def file_move(old_name, new_name):
    """
    Moves a file
    :param old_name: Fully qualified file path to file to be moved.
    :type old_name: str
    :param new_name: Fully qualified path to new file location and name.
    :type new_name: str
    :return: True file moved, otherwise False
    :rtype: bool
    """

    value = True
    try:
        shutil.move(old_name, new_name)
    except Exception:
        value = False
    return value


def move_all_files_from_dir_to_dir(src_dir, dest_dir):
    """
    Moves all files from one directory to another.
    :param src_dir: Source directory path
    :type src_dir: str
    :param dest_dir: Destination directory path
    :type dest_dir: str
    :return: True if moved, otherwise False
    :rtype: bool
    """

    value = True
    try:
        for file_name in os.listdir(src_dir):
            full_file_name = os.path.join(src_dir, file_name)
            if os.path.isfile(full_file_name):
                shutil.move(full_file_name, dest_dir)
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


def remove_backup_revit_files_from_list(files):
    """
    Takes a list of revit files or full paths and removes any backup files from the list.

    :param files: List of revit files or full paths
    :type files: list
    :return: List of revit files or full paths with backup files removed
    :rtype: list
    """
    files_not_backups = []
    # Exclude any files that are backups: they have .0001.rvt (or similar pattern) in their name
    for rvt_file in files:
        if not is_back_up_file(rvt_file):
            files_not_backups.append(rvt_file)

    return files_not_backups


def is_back_up_file(file_path):
    """
    Checks whether a file is a Revit back up file.

    Backup files are usually in format 'filename.01234.ext'

    Method of checking:

    - splitting file name at every full stop
    - check whether a list with more more then 2 entries came back ?

        - no:
            - not a back up
        - yes:
            - check last list entry whether it is 4 characters in length and can it be convert it into an integer?

                - yes:
                    - backup file
                - no
                    - normal file

    :param file_path: A fully qualified file path.
    :type file_path: str

    :return: True if a back up file, otherwise False.
    :rtype: bool
    """

    is_backup = False
    chunks = file_path.split(".")
    if len(chunks) > 2:
        last_chunk = chunks[len(chunks) - 2]
        try:
            if len(last_chunk) == 4:
                converted_num = int(last_chunk)
                is_backup = True
            else:
                is_backup = False
        except Exception:
            pass
    return is_backup


def remove_null_bytes(file_path, temp_file_path):
    """
    Remove null bytes from a source txt file and write to a temporary file.

    :param file_path: The path to the original txt file.
    :type file_path: str
    :param temp_file_path: The path to the temporary file where cleaned data is written.
    :type temp_file_path: str
    """
    with open(file_path, 'rb') as source_file:
        # Read the entire file and replace null bytes with an empty string
        content = source_file.read().replace(b'\0', b'')

    # Write content to a temporary file
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(content)



def is_last_char_newline(file_path):
    """
    Check if the last character in a file is a newline character.

    :param file_path: The fully qualified file path.
    :type file_path: str
    :return: True if the last character is a newline, otherwise False.
    :rtype: bool
    """

    # Function to check if the last character in the file is a newline
    # Check if the file exists
    if not os.path.exists(file_path):
        return False

    with open(file_path, 'rb') as file:
        # Seek to the last byte of the file
        file.seek(-1, os.SEEK_END)
        
        # Read the last byte and check if it's a newline character
        last_char = file.read(1)
        
        return last_char == b'\n'


def was_file_edited_in_time_span( file_path, time_span_in_minutes): 
    """
    Checks whether a file was edited in the given time span (in minutes) measured from current time.

    :param file_path: The fully qualified file path.
    :type file_path: str
    :param time_span_in_minutes: The time span in minutes.
    :type time_span_in_minutes: int

    :return: True if the file was edited in the given time span, otherwise False.
    :rtype: bool

    """
    
    was_edited = False
    try:
        time_diff_in_min = time_span_file_edited_last(file_path)
        
        # check if all went ok, if not return false
        if time_diff_in_min == -1:
            return False

        # check if file was edited in given time span
        if time_diff_in_min <= time_span_in_minutes:
            was_edited = True
    except Exception:
        pass
    return was_edited


def time_span_file_edited_last(file_path):
    """
    Returns the time span in minutes since the file was last edited measured from current time.

    :param file_path: The fully qualified file path.
    :type file_path: str

    :return: The time span in minutes since the file was last edited. -1 if an exception occurred.
    :rtype: int

    """
    
    time_span = -1
    try:
        current_time = time.time()
        file_mod_time = os.path.getmtime(file_path)
        time_diff = current_time - file_mod_time
        time_span = int(time_diff / 60)
    except Exception:
        pass
    return time_span