'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions relating to Revit worksharing monitor process. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Utilities import Utility as util
from duHast.Utilities import Result as res
from duHast.Utilities import SystemProcess as sp

''' 
Process name of work sharing monitor
'''

PROCESS_NAME_WSM = 'WorksharingMonitor.exe'
PROCESS_MARKER_FILENAME = 'WSMProcessList'
PROCESS_MARKER_FILE_EXTENSION = '.plist'


# --------------------------------- worksharing monitor specific ---------------------------------------

def GetWorkSharingMonitorProcesses():
    '''
    Get all currently running worksharing monitor processes

    :return: _description_
    :rtype: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    '''
    allProcesses = sp.GetAllRunningProcesses()
    wsmProcesses = sp.FilterByProcessName([PROCESS_NAME_WSM], allProcesses)
    return wsmProcesses

def WriteOutWSMDataToFile(directoryPath):
    '''
    Writes out all running worksharing monitor processes data to file

    :param directoryPath: The directory path to where the marker file is to be saved.
    :type directoryPath: str
    
    :return:  
        Result class instance.
        
        - Export status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain the fully qualified file path of the exported file.
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    status = res.Result()
    processList = GetWorkSharingMonitorProcesses()
    statusWriteOut = sp.WriteOutProcessData(directoryPath, processList, PROCESS_MARKER_FILENAME, PROCESS_MARKER_FILE_EXTENSION)
    if(statusWriteOut):
        status.UpdateSep(True, 'Successfully wrote WSM process marker file to: ' + str(directoryPath))
    else:
        status.UpdateSep(False, 'Failed to write WSM process marker file to: ' + str(directoryPath))
    return status

def DeleteWSMDataFiles(directoryPath):
    '''
    Deletes all WSM marker files in a directory.

    WSM marker files got a specific file extension: Check: PROCESS_MARKER_FILE_EXTENSION 

    :param directoryPath: The directory path containing marker files to be deleted.
    :type directoryPath: str

    :return: True if all files where deleted successfully, otherwise False.
    :rtype: bool
    '''

    status = True
    # get files in directory
    filesToDelete = util.GetFilesWithFilter(directoryPath, PROCESS_MARKER_FILE_EXTENSION)
    if(len(filesToDelete) > 0):
        statusDelete = True
        for file in filesToDelete:
            statusDelete = statusDelete and util.FileDelete(file)
    return status

def ReadWSMDataFromFile(directoryPath):
    '''
    Reads all worksharing monitor processes data from marker file(s) in a given directory
    
    WSM marker files got a specific file extension: Check: PROCESS_MARKER_FILE_EXTENSION 

    :param directoryPath: The directory path to where marker files are to be read from.
    :type directoryPath: str
    
    :return: list of list of str
    :rtype: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    '''
    
    processData = []
    files = util.GetFilesWithFilter(directoryPath, PROCESS_MARKER_FILE_EXTENSION)
    if(len(files) > 0):
        for file in files:
            rows = util.ReadCSVfile(file)
            if(len(rows)>0):
                processData = processData + rows
    return processData

def GetWSMSessionsToDelete(WSMsToKeep):
    '''
    Returns Worksharing monitor process sessions filtered by provided list (not in list)

    :param WSMsToKeep: List of worksharing monitor sessions to filter by. WSM included in this list will be removed from past in list.
    :type WSMsToKeep: List of list of str in format: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    
    :return: Filtered list of list of str of worksharing monitor sessions 
    :rtype: [[HandleCount, Name, Priority, ProcessId, ThreadCount, WorkingSetSize]]
    '''

    allRunningWSMProcesses = GetWorkSharingMonitorProcesses()
    if(len(WSMsToKeep) > 0):
        # get ids from list
        ids= []
        for wsmP in WSMsToKeep:
            ids.append(wsmP[3])
        filteredProcesses = sp.FilterByProcessIds(ids, WSMsToKeep, False)
        return filteredProcesses
    else:
        return allRunningWSMProcesses

def CleanUpWSMDataFiles(directoryPath):
    '''
    Removes all wsm data marker files in a given directory.

    WSM marker files got a specific file extension: Check: PROCESS_MARKER_FILE_EXTENSION.

    :param directoryPath: The directory path containing the marker files to be deleted.
    :type directoryPath: str
    
    :return:  
        Result class instance.
        
        - Delete status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will confirm successful deletion of all files.
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.

    :rtype: :class:`.Result`
    '''

    status = res.Result()
    # attempt to delete old marker files
    statusDelete = DeleteWSMDataFiles(directoryPath)
    if(statusDelete):
        status.UpdateSep(True,'Successfully deleted WSM marker file(s)!')
    else:
        status.UpdateSep(False,'Failed to delete WSM marker file(s)!')
    return status

def DieWSMDie(directoryPath, ignoreMarkerFiles = False):
    '''
    Kills all worksharing monitor processes currently active.

    Unless marker files are used. In that case only worksharing monitor sessions identified in marker files will be killed.

    :param directoryPath: The directory path to where marker files are to be read from.
    :type directoryPath: str
    :param ignoreMarkerFiles: True no marker file data will be read and all WSM sessions running will be killed., defaults to False
    :type ignoreMarkerFiles: bool, optional
    
    :return:  
        Result class instance.
        
        - Kill status returned in result.status. False if an exception occurred, otherwise True.
        - result.message will confirm successful killing of all WSM processes.
        
        On exception:
        
        - result.status (bool) will be False.
        - result.message will contain the exception message.
    
    :rtype: :class:`.Result`
    '''

    status = res.Result()
    try:
        wsmRunningPrior = []
        if(ignoreMarkerFiles == False):
            # read out worksharing monitor sessions running before script started
            wsmRunningPrior = ReadWSMDataFromFile(directoryPath)
        wsmToDelete = GetWSMSessionsToDelete(wsmRunningPrior)
        statusKill = sp.KillProcesses(wsmToDelete)
        if(statusKill):
            status.UpdateSep(True, 'All WSM sessions where killed.')
        else:
            status.UpdateSep(False, 'Failed to kill all WSM sessions.')
    except Exception as e:
        status.UpdateSep(False,'Failed to kill wsm sessions with exceptions: ' + str(e))
    return status