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
