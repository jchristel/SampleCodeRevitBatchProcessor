"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to directory IO . 
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
from os import path
import os.path
import shutil


def directory_empty_delete(full_directory_path):
    """
    Deletes an empty directory
    :param full_directory_path: Path to directory
    :type full_directory_path: str
    :return: True directory deleted, otherwise False
    :rtype: bool
    """

    try:
        os.rmdir(full_directory_path)
        value = True
    except Exception:
        value = False
    return value


def directory_delete(full_directory_path):
    """
    Deletes a directory (even if it contains files)
    :param full_directory_path: Path to directory
    :type full_directory_path: str
    :return: True directory deleted, otherwise False
    :rtype: bool
    """

    try:
        shutil.rmtree(full_directory_path)
        value = True
    except Exception as e:
        print(
            "When attempting to delete: {} an exception occurred: {}".format(
                full_directory_path, e
            )
        )
        value = False
    return value


def get_child_directories(full_directory_path):
    """
    Returns the immediate subdirectories of directory
    :param full_directory_path: Path to directory
    :type full_directory_path: str
    :return: any sub directories, empty list if none exist
    :rtype: list of str
    """

    sub_folders_with_paths = []
    for root, dirs, files in os.walk(full_directory_path):
        for dir in dirs:
            sub_folders_with_paths.append(os.path.join(root, dir))
        break
    return sub_folders_with_paths


def get_parent_directory(full_directory_path):
    """
    Returns the parent directory of directory, or empty string if invalid directory
    :param full_directory_path: Path to directory
    :type full_directory_path: str
    :return: parent directory, or empty string
    :rtype: str
    """

    parent_dir = ""
    try:
        parent_dir = os.path.dirname(full_directory_path)
    except Exception:
        pass
    return parent_dir


def create_directory(root, folder_name):
    """
    Create a folder.
    :param root: Directory path in which the new folder is to be created
    :type root: str
    :param folder_name: New folder name.
    :type folder_name: str
    :return: True if folder is created, otherwise False
    :rtype: bool
    """

    dir_name = path.join(root, folder_name)
    flag = True
    try:
        os.mkdir(dir_name)
    except Exception as e:
        # just in case the folder does exist (created by another instance at almost the same time)
        if "[Errno 17]" not in str(e):
            flag = False
    return flag


def create_target_directory(root_path, folder_name):
    """
    Create a folder.
    Checks whether folder exists and if not attempts to create it.

    :param root: Directory path in which the new folder is to be created
    :type root: str
    :param folder_name: New folder name.
    :type folder_name: str
    :return: True if folder is created, otherwise False
    :rtype: bool
    """

    # check if folder exists
    flag = True
    if path.exists(root_path + "\\" + folder_name) == False:
        # create new folder
        flag = create_directory(root_path, folder_name)
    return flag


def directory_exists(directory_path):
    """
    Check if a given directory exists
    :param directory_path: Fully qualified directory path
    :type directory_path: str
    :return: True if directory exists, otherwise False
    :rtype: bool
    """
    if path.exists(directory_path):
        return True
    else:
        return False
