'''
This module contains a number of functions around Revit BIM360. 
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
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

import System
import clr
import Utility as util

#from System.IO import Path
from Autodesk.Revit.DB import ModelPathUtils


# return human readable BIM 360 path
def GetBim360Path(doc):
    # get bim 360 path
    revitFilePath = ''
    try:
        path = doc.GetCloudModelPath()
        revitFilePath = ModelPathUtils.ConvertModelPathToUserVisiblePath(path)
    except Exception as e:
        revitFilePath = ''
    return revitFilePath

# pretend this is a file server path rather than cloud model path
def ConvertBIM360FilePath(path):
    # hack.. pretend path points to C:\\ rather than BIM 360://
    path = path.replace(r'BIM 360://', r'C:/')
    return path

# doc       current model document
def GetModelBIM360Ids(doc):
    '''returns project id, model id, human readable path'''
    path = doc.GetCloudModelPath()
    modelGuid = path.GetModelGUID()
    projectGuid = path.GetProjectGUID()
    # check whether this is a cloud model
    isCloudModel = path.CloudPath
    # get human reeadable path
    human = ModelPathUtils.ConvertModelPathToUserVisiblePath(path)
    return projectGuid,modelGuid,str(human)

# doc       current model document
def GetModelFileSize(doc):
    '''returns BIM360 file size, if file not exists on local cache it will return -1'''
    fileSize = -1
    path = doc.GetCloudModelPath()
    fullPath = ModelPathUtils.ConvertModelPathToUserVisiblePath(path)
    if (fullPath.StartsWith("BIM 360")):
        # get user envirnoment
        hostName = util.GetLocalAppDataPath()
        # build path to local cache files
        folder = hostName + '\\Autodesk\\Revit\\Autodesk Revit ' + str(doc.Application.VersionNumber) + '\\CollaborationCache'
        # local cache file name is same as file GUID on BIM360
        revitFile = doc.WorksharingCentralGUID.ToString()
        # get all files in cache folder matching GUID
        file_list = util.GetFilesFromDirectoryWalker(folder, revitFile)
        if (len(file_list) > 0):
            for file in file_list:
                # just select one of the file instance..not to sure why this one?
                if (file.Contains('CentralCache') == False):
                    fileSize = util.GetFileSize(file)
                    break
    return fileSize