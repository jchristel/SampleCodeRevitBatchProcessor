'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to Solibri IFC optimizer.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List of imports:

- :class:`.Result`
- :module: Utility

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


import subprocess
from System.IO import Path

from duHast.Utilities import Result as res, FilesGet as fileGet, FilesIO as util


#: The default install path for solibri ifc optimizer.
solibriInstallPath_ = r'C:\Program Files\Solibri\IFCOptimizer\Solibri IFC Optimizer.exe'

def optimize_all_ifc_files_in_directory(directoryPath):
    '''
    Function applying third party IFC optimizer to all ifc files in a given folder.

    Original files will be deleted.

    :param directoryPath: The directory path where IFC files are located
    :type directoryPath: str
    :return: 
        Result class instance.

        - Optimizer status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path(s) of the optimized file(s).
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
    
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # check if ifc optimizer is installed:
    if(util.file_exist(solibriInstallPath_)):
        returnValue.message = 'Solibri IFC optimizer is installed.'
        ifcFiles = fileGet.get_files(directoryPath, '.ifc')
        if(len(ifcFiles) > 0):
            processFilesResult = process_ifc_files(ifcFiles, directoryPath)
            returnValue.update(processFilesResult)
        else:
            returnValue.append_message('No IFC files found in directory: '+ str(directoryPath))
    else:
        returnValue.update_sep(False, 'No IFC optimizer installed at: '+ str(solibriInstallPath_))
    return returnValue

def optimize_ifc_files_in_list(ifcFiles, directoryPath):
    '''
    This function will optimize all IFC files in a given list of fully qualified file path to ifc files.

    Will check whether Solibri IFC optimizer is installed.

    :param ifcFiles: List containing fully qualified file path of ifc files to be optimized.
    :type ifcFiles: list of str
    :param directoryPath: Directory of where the optimized IFC file(s) are to be saved.
    :type directoryPath: str
    
    :return: 
        Result class instance.

        - Optimizer status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path(s) of the optimized file(s).
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.

    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    # check if ifc optimizer is installed:
    if(util.file_exist(solibriInstallPath_)):
        returnValue.message = 'Solibri IFC optimizer is installed.'
        if(len(ifcFiles) > 0):
            processFilesResult = process_ifc_files(ifcFiles, directoryPath)
            returnValue.update(processFilesResult)
        else:
            returnValue.append_message('IFC file list is empty.')
    else:
        returnValue.update_sep(False, 'No IFC optimizer installed at: '+ str(solibriInstallPath_))
    return returnValue

def process_ifc_files(ifcFiles, directoryPath):
    '''
    This function will optimize all IFC files in a given list of fully qualified file path to ifc files.

    Will not check whether Solibri IFC optimizer is installed.
    
    :param ifcFiles: List containing fully qualified file path of ifc files to be optimized.
    :type ifcFiles: list of str
    :param directoryPath: Directory of where the optimized IFC file(s) are to be saved.
    :type directoryPath: str
    
    :return: 
        Result class instance.

        - Optimizer status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path(s) of the optimized file(s).
        
        On exception (handled by optimizer itself!):
        
        - result.status (bool) will be False.
        - result.message will contain generic exception message.
        
    :rtype: :class:`.Result`
    '''

    returnValue = res.Result()
    filesToDelete = []
    filesToRename = []
    if(len(ifcFiles) > 0):
        returnValue.append_message('found ifc files: ' + str(len(ifcFiles)))
        for ifcFile in ifcFiles:
            s = subprocess.check_call([r'C:\Program Files\Solibri\IFCOptimizer\Solibri IFC Optimizer.exe', '-in=' + ifcFile, '-out=' + directoryPath, '-ifc', '-force'])
            # check what came back
            if (s == 0):
                # all went ok:
                returnValue.append_message('Optimized file: '+str(ifcFile))
                filesToDelete.append(ifcFile) # full file path
                # get the rename information
                # contains old and new file name
                rename = []
                p = util.get_directory_path_from_file_path(ifcFile)
                if(p != ''):
                    newFilePath = str(p)+'\\'+ str(Path.GetFileNameWithoutExtension(ifcFile))+'_optimized.ifc'
                    rename.append(newFilePath)
                    rename.append(ifcFile)
                    filesToRename.append(rename)
            else:
                    # something went wrong
                    returnValue.update_sep(False, 'Failed to optimize file: '+ str(ifcFile))
        # clean up
        for fileToDelete in filesToDelete:
            statusDelete = util.file_delete(fileToDelete)
            if(statusDelete):
                returnValue.append_message('Deleted original file: ' + str(fileToDelete))
            else:
                returnValue.update_sep(False,'Failed to delete original file: '+ str(fileToDelete))
        for fileToRename in filesToRename:
            statusRename = util.rename_file(fileToRename[0], fileToRename[1])
            if(statusRename):
                returnValue.append_message('Renamed original file: ' + str(fileToRename[0]) + ' to: ' + str(fileToRename[1]))
            else:
                returnValue.update_sep(False,'Failed to rename original file: '+ str(fileToRename[0]))
    else:
        returnValue.append_message('No IFC files found')
    return returnValue
