import os
from os import path
import os.path
import shutil


def DirectoryEmptyDelete(fullDirectoryPath):
    '''
    Deletes an empty directory
    :param fullDirectoryPath: Path to directory
    :type fullDirectoryPath: str
    :return: True directory deleted, otherwise False
    :rtype: bool
    '''

    try:
        os.rmdir(fullDirectoryPath)
        value = True
    except Exception:
        value = False
    return value


def DirectoryDelete(fullDirectoryPath):
    '''
    Deletes a directory (even if it contains files)
    :param fullDirectoryPath: Path to directory
    :type fullDirectoryPath: str
    :return: True directory deleted, otherwise False
    :rtype: bool
    '''

    try:
        shutil.rmtree(fullDirectoryPath)
        value = True
    except Exception as e:
        print('An exception occurred when attempting to delete a directory: ' + str(e))
        value = False
    return value


def GetChildDirectories(fullDirectoryPath):
    '''
    Returns the immediate subdirectories of directory
    :param fullDirectoryPath: Path to directory
    :type fullDirectoryPath: str
    :return: any sub directories, empty list if none exist
    :rtype: list of str
    '''

    subFoldersWithPaths = []
    for root, dirs, files in os.walk(fullDirectoryPath):
        for dir in dirs:
            subFoldersWithPaths.append( os.path.join(root, dir) )
        break
    return subFoldersWithPaths


def GetParentDirectory(fullDirectoryPath):
    '''
    Returns the parent directory of directory, or empty string if invalid directory
    :param fullDirectoryPath: Path to directory
    :type fullDirectoryPath: str
    :return: parent directory, or empty string
    :rtype: str
    '''

    parentDir = ''
    try:
        parentDir = os.path.dirname(fullDirectoryPath)
    except Exception:
        pass
    return parentDir


def CreateFolder(root, folderName):
    '''
    Create a folder.
    :param root: Directory path in which the new folder is to be created
    :type root: str
    :param folderName: New folder name.
    :type folderName: str
    :return: True if folder is created, otherwise False
    :rtype: bool
    '''

    dirName = path.join(root,folderName)
    flag = True
    try:
        os.mkdir(dirName)
    except Exception as e:
        # just in case the folder does exist (created by another instance at almost the same time)
        if('[Errno 17]' not in str(e)):
            flag = False
    return flag


def CreateTargetFolder(rootPath, folderName):
    '''
    Create a folder.
    Checks whether folder exists and if not attempts to create it.
    :param root: Directory path in which the new folder is to be created
    :type root: str
    :param folderName: New folder name.
    :type folderName: str
    :return: True if folder is created, otherwise False
    :rtype: bool
    '''

    #check if folder exists
    flag = True
    if(path.exists(rootPath + '\\' + folderName) == False):
        #create new folder
        flag = CreateFolder(rootPath, folderName)
    return flag


def DirectoryExists(directoryPath):
    '''
    Check if a given directory exists
    :param directoryPath: Fully qualified directory path
    :type directoryPath: str
    :return: True if directory exists, otherwise False
    :rtype: bool
    '''
    if(path.exists(directoryPath)):
        return True
    else:
        return False