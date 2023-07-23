"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Functions around Revit BIM360.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

import System
import clr
from duHast.Utilities import files_get as fileGet, files_io as fileIO, utility as util

# from System.IO import Path
import Autodesk.Revit.DB as rdb


def get_bim_360_path(doc):
    """
    Gets human readable BIM 360 path.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: The path to the bim360 model. If an exception occurred an empty string will be returned.
    :rtype: str
    """

    # get bim 360 path
    revit_file_path = ""
    try:
        path = doc.GetCloudModelPath()
        revit_file_path = rdb.ModelPathUtils.ConvertModelPathToUserVisiblePath(path)
    except Exception as e:
        revit_file_path = ""
    return revit_file_path


def convert_bim_360_file_path(path):
    """
    Pretend this is a file server path rather than cloud model path and swap cloud path with C:/

    :param path: The model cloud file path starting with BIM360
    :type path: str

    :return: A file path without BIM360
    :rtype: str
    """

    # hack.. pretend path points to C:\\ rather than BIM 360:// or 'autodesk docs://'
    if path.lower().startswith("bim 360://"):
        # bim 360 naming
        path = r"C:/" + path[len("bim 360://") :]
    elif path.lower().startswith("autodesk docs://"):
        # autodesk construction cloud naming
        path = r"C:/" + path[len("autodesk docs://") :]
    return path


def get_model_bim_360_ids(doc):
    """
    Gets project id, model id, human readable path from the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: project GUID, model GUID, human readable cloud path
    :rtype: GUID, GUID, str
    """

    path = doc.GetCloudModelPath()
    model_guid = path.GetModelGUID()
    project_guid = path.GetProjectGUID()
    # check whether this is a cloud model
    is_cloud_model = path.CloudPath
    # get human readable path
    human = rdb.ModelPathUtils.ConvertModelPathToUserVisiblePath(path)
    return project_guid, model_guid, str(human)


def get_model_file_size(doc):
    """
    Gets BIM360 file size, if file does not exists on local cache it will return -1.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: If file exists the file size in MB, otherwise -1
    :rtype: float
    """

    file_size = -1
    path = doc.GetCloudModelPath()
    full_path = rdb.ModelPathUtils.ConvertModelPathToUserVisiblePath(path)
    if full_path.StartsWith("BIM 360"):
        # get user environment
        host_name = util.get_local_app_data_path()
        # build path to local cache files
        folder = (
            host_name
            + "\\Autodesk\\Revit\\Autodesk Revit "
            + str(doc.Application.VersionNumber)
            + "\\CollaborationCache"
        )
        # local cache file name is same as file GUID on BIM360
        revit_file = doc.WorksharingCentralGUID.ToString()
        # get all files in cache folder matching GUID
        file_list = fileGet.get_files_from_directory_walker(folder, revit_file)
        if len(file_list) > 0:
            for file in file_list:
                # just select one of the file instance..not to sure why this one?
                if file.Contains("CentralCache") == False:
                    file_size = fileIO.get_file_size(file)
                    break
    return file_size
