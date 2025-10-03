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
from os import path
import os.path
import shutil
import uuid

# net import for directory delete with fall back
from System.IO import Directory, IOException
from System.Threading import Thread

def is_directory(directory_path):
    """
    Check if a given path is a directory
    :param directory_path: Fully qualified directory path
    :type directory_path: str
    :return: True if directory, otherwise False
    :rtype: bool
    """
    try:
        return os.path.isdir(directory_path)
    except Exception:
        return False


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
        return  True
    except Exception as e:
        return  False


def directory_delete_with_fallback(full_directory_path, max_attempts=3, delay_ms=100):
    """
    Deletes a directory (even if it contains files)
    If it fails, it will try again after a short wait

    :param full_directory_path: Path to directory
    :type full_directory_path: str
    :param max_attempts: Number of attempts to delete the directory
    :type max_attempts: int
    :param delay_ms: Delay in milliseconds between attempts
    :type delay_ms: int
    :return: True directory deleted, otherwise False
    :rtype: bool
    """

    for attempt in range(max_attempts):
        try:
            if Directory.Exists(full_directory_path):
                # delete if it exists
                Directory.Delete(full_directory_path, True)
                return True
            else:
                # already gone
                return True
        except IOException as e:
            if attempt < max_attempts - 1:
                # wait a bit before retrying
                Thread.Sleep(delay_ms)
            else:
                # last attempt failed
                return False
        except Exception as e:
            # something went wrong
            return False




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


def get_all_nested_directories(full_directory_path):
    # returns all nested direcory paths
    """
    Returns all nested directories of directory

    :param full_directory_path: Path to directory
    :type full_directory_path: str
    :return: any sub directories, empty list if none exist
    :rtype: list of str
    """

    nested_directories = []
    for entry in os.listdir(full_directory_path):
        full_path = os.path.join(full_directory_path, entry)
        if os.path.isdir(full_path):
            nested_directories.append(full_path)
            nested_directories.extend(get_all_nested_directories(full_path))
    return nested_directories


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


def create_nested_directory(directory_path):
    """
    Creates a directory and all necessary subdirectories.

    :param directory_path: Fully qualified directory path
    :type directory_path: str
    
    :return: True if directory is created, otherwise False
    :rtype: bool
    """
    try:
        import clr
        clr.AddReference("System")
        from System.IO import Directory

        # Create the directory and all necessary subdirectories
        Directory.CreateDirectory(directory_path)

        return True
    except Exception:

        return False


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



def get_current_user_documents_directory():
    """
    Get the current user's documents directory.

    :return: Path to the user's documents directory.
    :rtype: str
    """
    
    import clr
    clr.AddReference("System")
    from System import Environment

    # Get the user's Documents folder path
    documents_path = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments)

    return documents_path


def create_temp_directory(root_directory=None):
    """
    Creates a temporary directory in the system temp folder.

    :param root_directory: Root directory to create the temp folder in. If None, uses the system temp folder.
    :type root_directory: str or None. If none provided, the user's documents folder is used.
    :return: Path to the created temporary directory.
    :rtype: str
    """
    
    # Generate a random filename
    random_filename = uuid.uuid4().hex  # Creates a unique random string

    # If no root directory is provided, use the users doc folder
    if root_directory is None:
        root_directory = get_current_user_documents_directory()
    
    temp_directory = os.path.join(root_directory, random_filename)
    # Check if the directory exists before creating
    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)
        
    
    return temp_directory
