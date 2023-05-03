'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to file IO operations. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import os
import os.path
import shutil

#from System.IO import Path


def file_exist(full_file_path):
    '''
    Checks whether a file exists
    :param full_file_path: Fully qualified file path
    :type full_file_path: str
    :return: True file exists, otherwise False
    :rtype: bool
    '''

    try:
        value = os.path.exists(full_file_path)
    except Exception:
        value = False
    return value


def file_delete(full_file_path):
    '''
    Deletes file.

    :param full_file_path: Fully qualified file path
    :type full_file_path: str
    :return: True if deleted, otherwise False
    :rtype: bool
    '''
    try:
        os.remove(full_file_path)
        value = True
    except Exception:
        value = False
    return value


def get_directory_path_from_file_path(file_path):
    '''
    Extracts directory from file path.
    
    :param file_path: A fully qualified file path.
    :type file_path: str
    :return: If no exception occurs : A fully qualified directory path,else an empty string.
    :rtype: str
    '''
    try:
        value = os.path.dirname(file_path)
    except Exception:
        value = ''
    return value


def rename_file(old_name, new_name):
    '''
    Renames a file.
    :param old_name: Fully qualified file path to file to be renamed.
    :type old_name: str
    :param new_name: Fully qualified new file name.
    :type new_name: str
    :return: True file renamed, otherwise False
    :rtype: bool
    '''

    try:
        os.rename(old_name, new_name)
        value = True
    except Exception:
        value = False
    return value


def copy_file(old_name, new_name):
    '''
    Copies a file
    :param old_name: Fully qualified file path to file to be copied.
    :type old_name: str
    :param new_name: Fully qualified path to new file location and name.
    :type new_name: str
    :return: True file copied, otherwise False
    :rtype: bool
    '''

    value = True
    try:
        shutil.copy(old_name, new_name)
    except Exception:
        value = False
    return value

#: file size in KB conversion
FILE_SIZE_IN_KB = 1024
#: file size in MB conversion
FILE_SIZE_IN_MB = 1024*1024
#: file size in GB conversion
FILE_SIZE_IN_GB = 1024*1024*1024

def get_file_size(file_path, unit = FILE_SIZE_IN_MB):
    '''
    Get the file size in given units (default is MB)
    :param file_path: Fully qualified file path
    :type file_path: str
    :param unit: the file size unit, defaults to FILE_SIZE_IN_MB
    :type unit: int
    :return: The file size.
    :rtype: float
    '''

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
    '''
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
    '''

    if( r'..\..' in relative_file_path):
        two_up = path.abspath(path.join(full_file_path ,r'..\..'))
        return two_up + relative_file_path[5:]
    elif('..' in relative_file_path):
        one_up = path.abspath(path.join(full_file_path ,'..'))
        return one_up + relative_file_path[2:]
    else:
        return relative_file_path


def get_file_name_without_ext(file_path):
    '''
    Returns the file name without the file extension.

    :param file_path: Fully qualified file path to file
    :type file_path: str
    :return: The file name.
    :rtype: str
    '''

    file_name = os.path.basename(file_path)
    name_chunks = file_name.split('.')
    name = ''
    if(len(name_chunks)>1):
        name = '.'.join(name_chunks[:-1])
    else:
        name = file_name
    return name


def get_first_row_in_file(file_path):
    '''
    Reads the first line of a text file and returns it as a single string
    
    :param file_path: The fully qualified file path.
    :type file_path: str
    :return: The first row of a text file.
    :rtype: str
    '''

    row = ''
    try:
        with open(file_path) as f:
            row = f.readline().strip()
    except Exception:
        row = None
    return row