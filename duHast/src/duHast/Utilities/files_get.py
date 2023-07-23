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
