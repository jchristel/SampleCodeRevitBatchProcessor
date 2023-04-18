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
from os import path
import os.path
import shutil

from System.IO import Path


def file_exist(fullFilePath):
    '''
    Checks whether a file exists
    :param fullFilePath: Fully qualified file path
    :type fullFilePath: str
    :return: True file exists, otherwise False
    :rtype: bool
    '''

    try:
        value = os.path.exists(fullFilePath)
    except Exception:
        value = False
    return value


def file_delete(fullFilePath):
    try:
        os.remove(fullFilePath)
        value = True
    except Exception:
        value = False
    return value


def get_directory_path_from_file_path(filePath):
    '''
    Extracts directory from file path.
    :param filePath: A fully qualified file path.
    :type filePath: str
    :return: If no exception occurs : A fully qualified directory path,else an empty string.
    :rtype: str
    '''
    try:
        value = os.path.dirname(filePath)
    except Exception:
        value = ''
    return value


def rename_file(oldName, newName):
    '''
    Renames a file.
    :param oldName: Fully qualified file path to file to be renamed.
    :type oldName: str
    :param newName: Fully qualified new file name.
    :type newName: str
    :return: True file renamed, otherwise False
    :rtype: bool
    '''

    try:
        os.rename(oldName, newName)
        value = True
    except Exception:
        value = False
    return value


def copy_file(oldName, newName):
    '''
    Copies a file
    :param oldName: Fully qualified file path to file to be copied.
    :type oldName: str
    :param newName: Fully qualified path to new file location and name.
    :type newName: str
    :return: True file copied, otherwise False
    :rtype: bool
    '''

    value = True
    try:
        shutil.copy(oldName, newName)
    except Exception:
        value = False
    return value

#: file size in KB conversion
FILE_SIZE_IN_KB = 1024
#: file size in MB conversion
FILE_SIZE_IN_MB = 1024*1024
#: file size in GB conversion
FILE_SIZE_IN_GB = 1024*1024*1024

def get_file_size(filePath, unit = FILE_SIZE_IN_MB):
    '''
    Get the file size in given units (default is MB)
    :param filePath: Fully qualified file path
    :type filePath: str
    :param unit: the file size unit, defaults to FILE_SIZE_IN_MB
    :type unit: int
    :return: The file size.
    :rtype: float
    '''

    # default value if anything goes wrong
    size = -1
    try:
        size = os.path.getsize(filePath)
        # convert units
        size = size / unit
    except:
        pass
    return size


def convert_relative_path_to_full_path(relativeFilePath, fullFilePath):
    '''
    removes '../..' or '../' from relative file path string and replaces it with full path derived path past in sample path.
    - relative path sample: 'C:/temp/../myfile.ext'
    - full file path sample: 'C:/temp/Sample/someOtherFile.ext'
    - returns: 'C:/temp/Sample/myfile.ext'
    :param relativeFilePath: String containing relative file path annotation.
    :type relativeFilePath: str
    :param fullFilePath: A fully qualified file path of which the relative file path is a sub set.
    :type fullFilePath: str
    :return: A fully qualified file path.
    :rtype: str
    '''

    if( r'..\..' in relativeFilePath):
        two_up = path.abspath(path.join(fullFilePath ,r'..\..'))
        return two_up + relativeFilePath[5:]
    elif('..' in relativeFilePath):
        one_up = path.abspath(path.join(fullFilePath ,'..'))
        return one_up + relativeFilePath[2:]
    else:
        return relativeFilePath


def get_file_name_without_ext(filePath):
    '''
    Returns the file name without the file extension.
    :param filePath: Fully qualified file path to file
    :type filePath: str
    :return: The file name.
    :rtype: str
    '''

    name = Path.GetFileNameWithoutExtension(filePath)
    return name


def get_first_row_in_file(filePath):
    '''
    Reads the first line of a text file and returns it as a single string
    :param filePath: The fully qualified file path.
    :type filePath: str
    :return: The first row of a text file.
    :rtype: str
    '''

    row = ''
    try:
        with open(filePath) as f:
            row = f.readline().strip()
    except Exception:
        row = None
    return row