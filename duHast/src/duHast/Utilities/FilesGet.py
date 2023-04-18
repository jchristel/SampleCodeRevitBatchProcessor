'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to retrieving file information. 
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

import glob

from duHast.Utilities.FilesIO import get_file_name_without_ext
import os


def get_files_single_directory(folderPath, filePrefix, fileSuffix, fileExtension):
    '''
    Get files from a folder filtered by file prefix, file suffix, file extension
    :param folderPath: Folder path from which to get files.
    :type folderPath: str
    :param filePrefix: Filter: File name starts with this value.
    :type filePrefix: str
    :param fileSuffix: Filter: File name ends with this value.
    :type fileSuffix: str
    :param fileExtension: Filter: File needs to have this file extension
    :type fileExtension: str, format '.extension'
    :return: A list of all the files matching the supplied filters.
    :rtype: list str
    '''

    fileList = glob.glob(folderPath + '\\' + filePrefix + '*' + fileSuffix + fileExtension)
    return fileList


def get_files_from_directory_walker_with_filters(folderPath, filePrefix, fileSuffix, fileExtension):
    '''
    Returns a list of all files in directory and nested sub directories where file name matches filters value.
    :param folderPath: Root folder path from which to get files.
    :type folderPath: str
    :param filePrefix: Filter: File name starts with this value
    :type filePrefix: str
    :param fileSuffix: Filter: File name ends with this value.
    :type fileSuffix: str
    :param fileExtension: Filter: File needs to have this file extension
    :type fileExtension: str, format '.extension'
    :return: A list of all the files matching the supplied filters.
    :rtype: list str
    '''

    filesFound = []
    for root, dirs, files in os.walk(folderPath):
        for name in files:
            fileName = get_file_name_without_ext(name)
            if (name.endswith(fileExtension) and fileName.startswith(filePrefix) and fileName.endswith(fileSuffix)):
                filesFound.append(root + '\\' + name)
    return filesFound


def get_files_from_directory_walker_with_filters_simple(folderPath, fileExtension):
    '''
    Returns a list of all files in directory and nested subdirectories where file name matches file extension filter value
    :param folderPath: Root folder path from which to get files.
    :type folderPath: str
    :param fileExtension: Filter: File needs to have this file extension
    :type fileExtension: str, format '.extension'
    :return: A list of all the files matching the supplied filters.
    :rtype: list str
    '''

    filesFound = []
    filesFound = get_files_from_directory_walker_with_filters(folderPath, '', '', fileExtension)
    return filesFound


def files_as_dictionary(folderPath, filePrefix, fileSuffix, fileExtension, includeSubDirs = False):
    '''
    Returns a dictionary of all files in directory and nested subdirectories where file name contains filter value. 
    - key file name without extension
    - values: list of directories where this file occurs (based on file name only!)
    Use case: check for duplicates by file name only
    :param folderPath: Root folder path from which to get files.
    :type folderPath: str
    :param filePrefix: Filter: File name starts with this value
    :type filePrefix: str
    :param fileSuffix: Filter: File name ends with this value.
    :type fileSuffix: str
    :param fileExtension: Filter: File needs to have this file extension
    :type fileExtension: str, format '.extension'
    :param includeSubDirs: If True subdirectories will be included in search for files, defaults to False
    :type includeSubDirs: bool, optional
    :return: A dictionary where the key is the file name without the file extension. Value is a list of fully qualified file path to instances of that file.
    :rtype: dictionary
        key: str
        value: lit of str
    '''

    filesFound = []
    # set up a dictionary
    fileDic = {}
    try:
        if(includeSubDirs):
            filesFound = get_files_from_directory_walker_with_filters(folderPath, '', '', '.rfa')
        else:
            filesFound = get_files_single_directory(folderPath, '', '', '.rfa')
    except Exception:
        return fileDic

    # populate dictionary
    for filePath in filesFound:
        fileName = get_file_name_without_ext(filePath)
        if(fileName in fileDic):
            fileDic[fileName].append(filePath)
        else:
            fileDic[fileName] = [filePath]
    return fileDic


def get_files(folderPath, fileExtension='.rvt'):
    '''
    Gets a list of files from a given folder with a given file extension
    :param folderPath: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folderPath: str
    :param fileExtension: Filter: File needs to have this file extension, defaults to '.rvt'
    :type fileExtension: str, optional
    :return: List of file path
    :rtype: list of str
    '''

    file_list = glob.glob(folderPath + '\\*' + fileExtension)
    return file_list


def get_files_with_filter(folderPath, fileExtension='.rvt', filter = '*'):
    '''
    Gets a list of files from a given folder with a given file extension and a matching a file name filter.

    :param folderPath: Folder path from which to get files.
    :type folderPath: str
    :param fileExtension: Filter: File needs to have this file extension, defaults to '.rvt'
    :type fileExtension: str, optional
    :param filter: File name filter ('something*'), defaults to '*'
    :type filter: str, optional
    :return: List of file path
    :rtype: list of str
    '''

    file_list = glob.glob(folderPath + '\\' + filter + fileExtension)
    return file_list


def get_files_from_directory_walker(path, filter):
    '''
    Gets all files in directory and nested subdirectories where file name contains filter value.

    :param path: Folder path from which to get files.
    :type path: str
    :param filter: File name filter ('something*')
    :type filter: str
    :return: List of file path
    :rtype: list of str
    '''

    filesFound = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if (name.Contains(filter)) :
                filesFound.append(root + '\\' + name)
    return filesFound