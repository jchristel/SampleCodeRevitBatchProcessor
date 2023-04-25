"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to retrieving file information. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
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

from duHast.Utilities.files_io import get_file_name_without_ext
import os


def get_files_single_directory(folder_path, file_prefix, file_suffix, file_extension):
    """
    Get files from a folder filtered by file prefix, file suffix, file extension
    :param folder_path: Folder path from which to get files.
    :type folder_path: str
    :param file_prefix: Filter: File name starts with this value.
    :type file_prefix: str
    :param file_suffix: Filter: File name ends with this value.
    :type file_suffix: str
    :param file_extension: Filter: File needs to have this file extension
    :type file_extension: str, format '.extension'
    :return: A list of all the files matching the supplied filters.
    :rtype: list str
    """

    fileList = glob.glob(
        os.path.join(folder_path, file_prefix + "*" + file_suffix + file_extension)
    )
    return fileList


def get_files_from_directory_walker_with_filters(
    folder_path, file_prefix, file_suffix, file_extension
):
    """
    Returns a list of all files in directory and nested sub directories where file name matches filters value.
    :param folder_path: Root folder path from which to get files.
    :type folder_path: str
    :param file_prefix: Filter: File name starts with this value
    :type file_prefix: str
    :param file_suffix: Filter: File name ends with this value.
    :type file_suffix: str
    :param file_extension: Filter: File needs to have this file extension
    :type file_extension: str, format '.extension'
    :return: A list of all the files matching the supplied filters.
    :rtype: list str
    """

    files_found = []
    for root, dirs, files in os.walk(folder_path):
        for name in files:
            file_name = get_file_name_without_ext(name)
            if (
                name.endswith(file_extension)
                and file_name.startswith(file_prefix)
                and file_name.endswith(file_suffix)
            ):
                files_found.append(os.path.join(root, name))
    return files_found


def get_files_from_directory_walker_with_filters_simple(folder_path, file_extension):
    """
    Returns a list of all files in directory and nested subdirectories where file name matches file extension filter value
    :param folder_path: Root folder path from which to get files.
    :type folder_path: str
    :param file_extension: Filter: File needs to have this file extension
    :type file_extension: str, format '.extension'
    :return: A list of all the files matching the supplied filters.
    :rtype: list str
    """

    files_found = []
    files_found = get_files_from_directory_walker_with_filters(
        folder_path, "", "", file_extension
    )
    return files_found


def files_as_dictionary(
    folder_path, file_prefix, file_suffix, file_extension, include_sub_dirs=False
):
    """
    Returns a dictionary of all files in directory and nested subdirectories where file name contains filter value.
    - key file name without extension
    - values: list of directories where this file occurs (based on file name only!)
    Use case: check for duplicates by file name only

    :param folder_path: Root folder path from which to get files.
    :type folder_path: str
    :param file_prefix: Filter: File name starts with this value
    :type file_prefix: str
    :param file_suffix: Filter: File name ends with this value.
    :type file_suffix: str
    :param file_extension: Filter: File needs to have this file extension
    :type file_extension: str, format '.extension'
    :param include_sub_dirs: If True subdirectories will be included in search for files, defaults to False
    :type include_sub_dirs: bool, optional
    :return: A dictionary where the key is the file name without the file extension. Value is a list of fully qualified file path to instances of that file.
    :rtype: dictionary
        key: str
        value: lit of str
    """

    files_found = []
    # set up a dictionary
    file_dic = {}
    try:
        if include_sub_dirs:
            files_found = get_files_from_directory_walker_with_filters(
                folder_path, file_prefix, file_suffix, file_extension
            )
        else:
            files_found = get_files_single_directory(
                folder_path, file_prefix, file_suffix, file_extension
            )
    except Exception:
        return file_dic

    # populate dictionary
    for file_path in files_found:
        file_name = get_file_name_without_ext(file_path)
        if file_name in file_dic:
            file_dic[file_name].append(file_path)
        else:
            file_dic[file_name] = [file_path]
    return file_dic


def get_files(folder_path, file_extension=".rvt"):
    """
    Gets a list of files from a given folder with a given file extension
    :param folder_path: Folder path from which to get files to be combined and to which the combined file will be saved.
    :type folder_path: str
    :param file_extension: Filter: File needs to have this file extension, defaults to '.rvt'
    :type file_extension: str, optional
    :return: List of file path
    :rtype: list of str
    """

    file_list = glob.glob(os.path.join(folder_path, "*" + file_extension))
    return file_list


def get_files_with_filter(folder_path, file_extension=".rvt", filter="*"):
    """
    Gets a list of files from a given folder with a given file extension and a matching a file name filter.

    :param folder_path: Folder path from which to get files.
    :type folder_path: str
    :param file_extension: Filter: File needs to have this file extension, defaults to '.rvt'
    :type file_extension: str, optional
    :param filter: File name filter ('something*'), defaults to '*'
    :type filter: str, optional
    :return: List of file path
    :rtype: list of str
    """

    file_list = glob.glob(os.path.join(folder_path, filter + file_extension))
    return file_list


def get_files_from_directory_walker(path, filter):
    """
    Gets all files in directory and nested subdirectories where file name contains filter value.

    :param path: Folder path from which to get files.
    :type path: str
    :param filter: File name filter ('something')
    :type filter: str
    :return: List of file path
    :rtype: list of str
    """

    file_list = glob.glob(os.path.join(path, "*" + filter + "*.*"), recursive=True)
    # files_found = []
    # for root, dirs, files in os.walk(path):
    #    for name in files:
    #        if (filter in name) :
    #            files_found.append(os.path.join(root, name))
    return file_list