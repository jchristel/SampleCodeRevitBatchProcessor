'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Functions around Revit BIM360.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
from duHast.Utilities import files_get as fileGet, files_io as fileIO, utility as util

#from System.IO import Path
import Autodesk.Revit.DB as rdb


def get_bim_360_path(doc):
    '''
    Gets human readable BIM 360 path.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: The path to the bim360 model. If an exception occurred an empty string will be returned.
    :rtype: str
    '''

    # get bim 360 path
    revit_file_path = ''
    try:
        path = doc.GetCloudModelPath()
        revit_file_path = rdb.ModelPathUtils.ConvertModelPathToUserVisiblePath(path)
    except Exception as e:
        revit_file_path = ''
    return revit_file_path

def convert_bim_360_file_path(path):
    '''
    Pretend this is a file server path rather than cloud model path and swap cloud path with C:/

    :param path: The model cloud file path starting with BIM360
    :type path: str

    :return: A file path without BIM360
    :rtype: str
    '''

    # hack.. pretend path points to C:\\ rather than BIM 360:// or 'autodesk docs://'
    if (path.lower().startswith('bim 360://')):
        # bim 360 naming
        path = r'C:/' + path[len('bim 360://'):]
    elif (path.lower().startswith('autodesk docs://')):
        # autodesk construction cloud naming
        path = r'C:/' + path[len('autodesk docs://'):]
    return path

def get_model_bim_360_ids(doc):
    '''
    Gets project id, model id, human readable path from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: project GUID, model GUID, human readable cloud path
    :rtype: GUID, GUID, str
    '''

    path = doc.GetCloudModelPath()
    model_guid = path.GetModelGUID()
    project_guid = path.GetProjectGUID()
    # check whether this is a cloud model
    is_cloud_model = path.CloudPath
    # get human readable path
    human = rdb.ModelPathUtils.ConvertModelPathToUserVisiblePath(path)
    return project_guid,model_guid,str(human)

def get_model_file_size(doc):
    '''
    Gets BIM360 file size, if file does not exists on local cache it will return -1.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    
    :return: If file exists the file size in MB, otherwise -1
    :rtype: float
    '''

    file_size = -1
    path = doc.GetCloudModelPath()
    full_path = rdb.ModelPathUtils.ConvertModelPathToUserVisiblePath(path)
    if (full_path.StartsWith("BIM 360")):
        # get user environment
        host_name = util.get_local_app_data_path()
        # build path to local cache files
        folder = host_name + '\\Autodesk\\Revit\\Autodesk Revit ' + str(doc.Application.VersionNumber) + '\\CollaborationCache'
        # local cache file name is same as file GUID on BIM360
        revit_file = doc.WorksharingCentralGUID.ToString()
        # get all files in cache folder matching GUID
        file_list = fileGet.get_files_from_directory_walker(folder, revit_file)
        if (len(file_list) > 0):
            for file in file_list:
                # just select one of the file instance..not to sure why this one?
                if (file.Contains('CentralCache') == False):
                    file_size = fileIO.get_file_size(file)
                    break
    return file_size